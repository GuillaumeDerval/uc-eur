#!/usr/bin/env julia
#
# Measure how much the transmission network costs in each instance, by solving
# it twice: once as generated, once with every flow limit multiplied by a large
# factor. The objective difference is the congestion cost -- what the grid, as
# opposed to the generation fleet, contributes to the bill.
#
#   julia --project=julia julia/congestion.jl <dir> [gap] [limit]

using UnitCommitment, JuMP, HiGHS, JSON, Printf, GZip

read_instance_json(path) =
    endswith(path, ".gz") ?
        GZip.open(path, "r") do io; JSON.parse(io; dicttype = Dict, inttype = Int64); end :
        JSON.parsefile(path; dicttype = Dict, inttype = Int64)
const HAS_GUROBI = try; @eval using Gurobi; true; catch; false; end

const dir = length(ARGS) >= 1 ? ARGS[1] : "instances"
const gap = length(ARGS) >= 2 ? parse(Float64, ARGS[2]) : 0.001
const limit = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 900.0
const RELAX = 10.0

make_opt() = HAS_GUROBI ?
    optimizer_with_attributes(Gurobi.Optimizer, "MIPGap" => gap,
                              "TimeLimit" => limit, "OutputFlag" => 0) :
    optimizer_with_attributes(HiGHS.Optimizer, "mip_rel_gap" => gap,
                              "time_limit" => limit, "output_flag" => false)

"""Solve one instance file, returning (objective, load shed MWh)."""
function solve_file(path)
    inst = UnitCommitment.read(path)
    opt = make_opt()
    any(g -> g.initial_power === nothing, inst.scenarios[1].thermal_units) &&
        UnitCommitment.generate_initial_conditions!(inst, opt)
    m = UnitCommitment.build_model(instance = inst, optimizer = opt)
    UnitCommitment.optimize!(m, UnitCommitment.XavQiuWanThi2019.Method(
        time_limit = limit, gap_limit = gap, two_phase_gap = false,
        max_violations_per_line = 5, max_violations_per_period = 50))
    has_values(m) || return (NaN, NaN)
    sol = UnitCommitment.solution(m)
    shed = sum(sum(v) for (_, v) in sol["Load curtail (MW)"]; init = 0.0)
    return (objective_value(m), shed)
end

function is_instance_file(f::AbstractString)
    (endswith(f, ".json") || endswith(f, ".json.gz")) || return false
    endswith(f, ".summary.json") && return false
    startswith(f, "results") && return false
    return f ∉ ("index.json", "congestion.json")
end

files = sort([joinpath(r, f) for (r, _, ns) in walkdir(dir) for f in ns
              if is_instance_file(f)])

@printf("%-28s %14s %14s %12s %10s\n",
        "instance", "objective", "uncongested", "congestion", "shed MWh")
results = Any[]
for f in files
    obj, shed = solve_file(f)
    # Same instance with the network effectively removed as a constraint.
    raw = read_instance_json(f)
    for l in values(raw["Transmission lines"])
        l["Normal flow limit (MW)"] *= RELAX
        l["Emergency flow limit (MW)"] *= RELAX
    end
    tmp = tempname() * ".json"
    open(tmp, "w") do io; JSON.print(io, raw, 1); end
    free_obj, _ = solve_file(tmp)
    rm(tmp, force = true)

    cong = obj - free_obj
    push!(results, Dict("file" => basename(f), "objective" => obj,
                        "uncongested" => free_obj, "congestion_cost" => cong,
                        "congestion_pct" => 100 * cong / free_obj,
                        "load_shed_MWh" => shed))
    @printf("%-28s %14.0f %14.0f %11.2f%% %10.1f\n",
            basename(f), obj, free_obj, 100 * cong / free_obj, shed)
    flush(stdout)
end
open(joinpath(dir, "congestion.json"), "w") do io
    JSON.print(io, results, 1)
end
