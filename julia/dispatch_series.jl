#!/usr/bin/env julia
#
# Solve instances and dump, per time step, the series a commitment plot needs:
# demand net of everything non-committable, and the capacity actually committed.
#
#   julia --project=julia julia/dispatch_series.jl <dir|file> [gap] [limit] [threads] [shard] [nshards]
#
# Writes <instance>.dispatch.json beside each instance.

using UnitCommitment, JuMP, HiGHS, JSON, Printf
const HAS_GUROBI = try; @eval using Gurobi; true; catch; false; end

const target  = length(ARGS) >= 1 ? ARGS[1] : "instances"
const gap     = length(ARGS) >= 2 ? parse(Float64, ARGS[2]) : 0.001
const limit   = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 1800.0
const threads = length(ARGS) >= 4 ? parse(Int, ARGS[4]) : 2
const shard   = length(ARGS) >= 5 ? parse(Int, ARGS[5]) : 1
const nshards = length(ARGS) >= 6 ? parse(Int, ARGS[6]) : 1

make_opt() = HAS_GUROBI ?
    optimizer_with_attributes(Gurobi.Optimizer, "MIPGap" => gap,
                              "TimeLimit" => limit, "Threads" => threads,
                              "OutputFlag" => 0) :
    optimizer_with_attributes(HiGHS.Optimizer, "mip_rel_gap" => gap,
                              "time_limit" => limit, "threads" => threads,
                              "output_flag" => false)

function is_instance_file(f::AbstractString)
    (endswith(f, ".json") || endswith(f, ".json.gz")) || return false
    endswith(f, ".summary.json") && return false
    endswith(f, ".dispatch.json") && return false
    startswith(f, "results") && return false
    return f ∉ ("index.json", "congestion.json")
end

function series(path::String)
    inst = UnitCommitment.read(path)
    sc, T = inst.scenarios[1], inst.time
    opt = make_opt()
    any(g -> g.initial_power === nothing, sc.thermal_units) &&
        UnitCommitment.generate_initial_conditions!(inst, opt)
    m = UnitCommitment.build_model(instance = inst, optimizer = opt)
    UnitCommitment.optimize!(m, UnitCommitment.XavQiuWanThi2019.Method(
        time_limit = limit, gap_limit = gap, two_phase_gap = false,
        max_violations_per_line = 5, max_violations_per_period = 50))
    has_values(m) || error("no primal solution ($(termination_status(m)))")
    sol = UnitCommitment.solution(m)

    load       = [sum(b.load[t] for b in sc.buses; init = 0.0) for t in 1:T]
    profiled   = [sum(sol["Profiled production (MW)"][p.name][t]
                      for p in sc.profiled_units; init = 0.0) for t in 1:T]
    thermal    = [sum(sol["Thermal production (MW)"][g.name][t]
                      for g in sc.thermal_units; init = 0.0) for t in 1:T]
    shed       = [sum(sol["Load curtail (MW)"][b.name][t]
                      for b in sc.buses; init = 0.0) for t in 1:T]
    charge = zeros(T); discharge = zeros(T)
    if !isempty(sc.storage_units)
        charge    = [sum(sol["Storage charging rates (MW)"][s.name][t]
                         for s in sc.storage_units; init = 0.0) for t in 1:T]
        discharge = [sum(sol["Storage discharging rates (MW)"][s.name][t]
                         for s in sc.storage_units; init = 0.0) for t in 1:T]
    end
    # Capacity of the units switched on, and the floor those units impose.
    committed = [sum(g.max_power[t] * (sol["Is on"][g.name][t] > 0.5 ? 1 : 0)
                     for g in sc.thermal_units; init = 0.0) for t in 1:T]
    committed_min = [sum(g.min_power[t] * (sol["Is on"][g.name][t] > 0.5 ? 1 : 0)
                         for g in sc.thermal_units; init = 0.0) for t in 1:T]
    on_count = [count(g -> sol["Is on"][g.name][t] > 0.5, sc.thermal_units) for t in 1:T]

    return Dict(
        "time_steps" => T,
        "load_MW" => load,
        "profiled_MW" => profiled,
        "storage_charge_MW" => charge,
        "storage_discharge_MW" => discharge,
        "load_shed_MW" => shed,
        # What the committable fleet is left to serve.
        "residual_demand_MW" => load .- profiled .- discharge .+ charge .- shed,
        "thermal_production_MW" => thermal,
        "committed_capacity_MW" => committed,
        "committed_minimum_MW" => committed_min,
        "units_on" => on_count,
        "thermal_units" => length(sc.thermal_units),
        "objective" => objective_value(m),
        "status" => string(termination_status(m)),
    )
end

files = target |> t -> isfile(t) ? [t] :
    sort([joinpath(r, f) for (r, _, ns) in walkdir(t) for f in ns if is_instance_file(f)])
nshards > 1 && (files = files[shard:nshards:end])
@printf("dispatch series for %d instance(s) (%s)\n", length(files),
        HAS_GUROBI ? "Gurobi" : "HiGHS")

failed = 0
for (i, f) in enumerate(files)
    out = replace(f, r"\.json(\.gz)?$" => ".dispatch.json")
    try
        d = series(f)
        open(out, "w") do io; JSON.print(io, d, 1); end
        @printf("[%3d/%3d] %-38s peak residual %8.0f MW, peak committed %8.0f MW\n",
                i, length(files), basename(f),
                maximum(d["residual_demand_MW"]), maximum(d["committed_capacity_MW"]))
    catch e
        global failed += 1
        @printf("[%3d/%3d] %-38s FAILED: %s\n", i, length(files), basename(f),
                sprint(showerror, e))
    end
    flush(stdout)
end
@printf("\n%d/%d written\n", length(files) - failed, length(files))
