#!/usr/bin/env julia
#
# Solve a directory of generated instances and check each reaches a schedule
# with no load shedding. Cost optimality is not required, so the MIP gap is
# deliberately loose.
#
#   julia --project=julia julia/solve_all.jl instances [gap] [time_limit_s] [threads]
#
# Writes instances/results.json and prints a per-instance line.

using UnitCommitment, JuMP, HiGHS, JSON, Printf, Dates

# Gurobi is far faster than HiGHS on these MILPs; use it when a licence is
# available and fall back to HiGHS otherwise.
const HAS_GUROBI = try
    @eval using Gurobi
    true
catch
    false
end

function make_optimizer(; gap, limit, threads, quiet = true)
    if HAS_GUROBI
        return optimizer_with_attributes(
            Gurobi.Optimizer,
            "MIPGap" => gap, "TimeLimit" => limit,
            "Threads" => threads, "OutputFlag" => quiet ? 0 : 1,
        )
    end
    return optimizer_with_attributes(
        HiGHS.Optimizer,
        "mip_rel_gap" => gap, "time_limit" => limit,
        "threads" => threads, "output_flag" => !quiet,
    )
end

const dir = length(ARGS) >= 1 ? ARGS[1] : "instances"
const gap = length(ARGS) >= 2 ? parse(Float64, ARGS[2]) : 0.001
const limit = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 900.0
const threads = length(ARGS) >= 4 ? parse(Int, ARGS[4]) : 1
# Optional sharding so several processes can split the set: shard is 1-based.
const shard = length(ARGS) >= 5 ? parse(Int, ARGS[5]) : 1
const nshards = length(ARGS) >= 6 ? parse(Int, ARGS[6]) : 1

"""
Power balance recomputed with curtailment included.

UnitCommitment.jl 0.4.2's own `validate` under-reports this: validate.jl wraps a
single-scenario solution as Dict("s1" => solution) at line 32, then guards the
curtailment term with `"Load curtail (MW)" in keys(solution)` at line 569, which
tests the wrapped dict whose only key is "s1". The term is therefore always
zero and every solution that sheds load looks unbalanced.
"""
function balance_residual(instance, solution)
    sc = instance.scenarios[1]
    worst = 0.0
    for t in 1:instance.time
        load = sum(b.load[t] for b in sc.buses; init = 0.0)
        curtail = sum(
            solution["Load curtail (MW)"][b.name][t] for b in sc.buses; init = 0.0
        )
        prod = sum(
            solution["Thermal production (MW)"][g.name][t] for g in sc.thermal_units;
            init = 0.0,
        )
        prod += sum(
            solution["Profiled production (MW)"][p.name][t] for p in sc.profiled_units;
            init = 0.0,
        )
        charge = discharge = 0.0
        if !isempty(sc.storage_units)
            charge = sum(
                solution["Storage charging rates (MW)"][s.name][t] for
                s in sc.storage_units; init = 0.0
            )
            discharge = sum(
                solution["Storage discharging rates (MW)"][s.name][t] for
                s in sc.storage_units; init = 0.0
            )
        end
        r = load - curtail - prod + charge - discharge
        abs(r) > abs(worst) && (worst = r)
    end
    return worst
end

"""
Instances are generated without an initial commitment state: there is no
dataset of what was running the hour before a chosen week, and asserting one
distorts the answer (cold-starting a national fleet forces load shedding that
reflects the assumption, not the power system).

UnitCommitment.jl's `build_model` requires the state, so derive a feasible,
self-consistent one from the instance itself with the package's own
`generate_initial_conditions!`, which solves a single-period MIP against the
first hour's demand.
"""
function ensure_initial_conditions!(instance, optimizer)
    sc = instance.scenarios[1]
    needs = any(
        g -> g.initial_power === nothing || g.initial_status === nothing,
        sc.thermal_units,
    )
    needs || return false
    UnitCommitment.generate_initial_conditions!(instance, optimizer)
    return true
end

function solve_one(path::String)
    result = Dict{String,Any}("file" => path)
    try
        instance = UnitCommitment.read(path)
        sc = instance.scenarios[1]
        result["buses"] = length(sc.buses)
        result["thermal_units"] = length(sc.thermal_units)
        result["profiled_units"] = length(sc.profiled_units)
        result["lines"] = length(sc.lines)
        result["time"] = instance.time

        optimizer = make_optimizer(gap = gap, limit = limit, threads = threads)
        result["initial_conditions_generated"] =
            ensure_initial_conditions!(instance, optimizer)
        model = UnitCommitment.build_model(instance = instance, optimizer = optimizer)
        # UnitCommitment.optimize!(model) uses XavQiuWanThi2019.Method defaults, whose
        # time_limit is 86400s and whose gap_limit is 1e-3 -- both override the
        # attributes set on the optimizer above, so pass them explicitly.
        elapsed = @elapsed UnitCommitment.optimize!(
            model,
            UnitCommitment.XavQiuWanThi2019.Method(
                time_limit = limit,
                gap_limit = gap,
                two_phase_gap = false,
                # The default adds only 1 violated constraint per line and 5 per
                # period, so a 168-period instance needs ~10 full MILP re-solves.
                # Adding more per round trades a slightly larger model for far
                # fewer resolves.
                max_violations_per_line = 5,
                max_violations_per_period = 50,
            ),
        )

        status = string(termination_status(model))
        result["status"] = status
        result["solve_seconds"] = round(elapsed, digits = 1)
        if !has_values(model)
            result["ok"] = false
            result["reason"] = "no primal solution ($status)"
            return result
        end
        result["objective"] = round(objective_value(model), digits = 2)

        solution = UnitCommitment.solution(model)
        demand = sum(sum(b.load) for b in sc.buses; init = 0.0)
        shed = sum(sum(v) for (_, v) in solution["Load curtail (MW)"]; init = 0.0)
        residual = balance_residual(instance, solution)

        result["demand_MWh"] = round(demand, digits = 1)
        result["load_shed_MWh"] = round(shed, digits = 3)
        result["load_shed_pct"] = round(100 * shed / demand, digits = 5)
        result["max_balance_residual_MW"] = round(residual, digits = 6)
        # A megawatt-hour over a whole week is numerical dust, not shed load.
        result["ok"] = shed <= 1.0 && abs(residual) <= 1e-3
        result["reason"] = result["ok"] ? "" : "load shed $(round(shed, digits=2)) MWh"
    catch e
        result["ok"] = false
        result["status"] = "ERROR"
        result["reason"] = sprint(showerror, e)
    end
    return result
end

"""Instance files, as written by the generators; they may be gzipped."""
function is_instance_file(f::AbstractString)
    (endswith(f, ".json") || endswith(f, ".json.gz")) || return false
    endswith(f, ".summary.json") && return false
    startswith(f, "results") && return false
    return f ∉ ("index.json", "congestion.json")
end

files = String[]
for (root, _, names) in walkdir(dir), f in names
    if is_instance_file(f)
        push!(files, joinpath(root, f))
    end
end
sort!(files)
# Interleave so every shard gets a mix of large and small instances.
nshards > 1 && (files = files[shard:nshards:end])

@printf("shard %d/%d: %d instances (%s, gap %.1f%%, limit %.0fs, %d threads)\n\n",
        shard, nshards, length(files), HAS_GUROBI ? "Gurobi" : "HiGHS",
        100gap, limit, threads)

results = Any[]
for (i, f) in enumerate(files)
    r = solve_one(f)
    push!(results, r)
    mark = get(r, "ok", false) ? "ok  " : "FAIL"
    @printf("[%3d/%3d] %s %-34s %8s %7.1fs  shed %9.3f MWh (%.4f%%)\n",
            i, length(files), mark, basename(f),
            get(r, "status", "?"), get(r, "solve_seconds", 0.0),
            get(r, "load_shed_MWh", NaN), get(r, "load_shed_pct", NaN))
    flush(stdout)
end

ok = count(r -> get(r, "ok", false), results)
const outfile = nshards > 1 ? "results.shard$(shard).json" : "results.json"
open(joinpath(dir, outfile), "w") do io
    JSON.print(io, Dict(
        "solver" => HAS_GUROBI ? "Gurobi" : "HiGHS",
        "mip_rel_gap" => gap,
        "time_limit_s" => limit,
        "generated" => string(now()),
        "instances" => length(results),
        "zero_shedding" => ok,
        "results" => results,
    ), 1)
end

@printf("\n%d/%d instances solved with no load shedding\n", ok, length(results))
for r in results
    get(r, "ok", false) || @printf("  FAIL %s: %s\n", basename(r["file"]), r["reason"])
end
exit(ok == length(results) ? 0 : 1)
