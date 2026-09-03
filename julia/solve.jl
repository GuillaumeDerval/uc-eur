#!/usr/bin/env julia
#
# End-to-end check: read a generated instance with UnitCommitment.jl, solve it,
# and validate the solution.
#
#   julia --project=julia julia/solve.jl instances/uc_BE_20190101_168h.json [gap] [time_limit_s]

using UnitCommitment, JuMP, HiGHS, Printf

path = length(ARGS) >= 1 ? ARGS[1] : error("usage: solve.jl <instance.json> [gap] [limit]")
gap = length(ARGS) >= 2 ? parse(Float64, ARGS[2]) : 1e-3
limit = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 600.0

@info "reading $path"
instance = UnitCommitment.read(path)

sc = instance.scenarios[1]
@printf("instance: %d buses, %d thermal units, %d profiled units, %d lines, T=%d\n",
        length(sc.buses), length(sc.thermal_units), length(sc.profiled_units),
        length(sc.lines), instance.time)
@printf("total thermal capacity: %.0f MW\n",
        sum(maximum(u.max_power) for u in sc.thermal_units; init = 0.0))
@printf("peak load:              %.0f MW\n",
        maximum(sum(b.load[t] for b in sc.buses) for t in 1:instance.time))

optimizer = optimizer_with_attributes(
    HiGHS.Optimizer,
    "mip_rel_gap" => gap,
    "time_limit" => limit,
)

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

if ensure_initial_conditions!(instance, optimizer)
    @info "derived feasible initial conditions (none asserted in the instance)"
end

@info "building model"
model = UnitCommitment.build_model(instance = instance, optimizer = optimizer)

@info "optimizing"
# UnitCommitment.optimize!(model) uses XavQiuWanThi2019.Method defaults, whose
# time_limit is 86400s and whose gap_limit is 1e-3 -- both override the
# attributes set on the optimizer above, so pass them explicitly.
elapsed = @elapsed UnitCommitment.optimize!(
    model,
    UnitCommitment.XavQiuWanThi2019.Method(
        time_limit = limit,
        gap_limit = gap,
        two_phase_gap = false,
    ),
)

status = termination_status(model)
@printf("\nstatus:       %s\n", status)
@printf("solve time:   %.1f s\n", elapsed)
if has_values(model)
    @printf("objective:    %.2f EUR\n", objective_value(model))
end

solution = UnitCommitment.solution(model)
UnitCommitment.write("solution.json", solution)

@info "validating solution against the instance"
uc_ok = UnitCommitment.validate(instance, solution)
@printf("UnitCommitment.validate: %s\n", uc_ok)

# NOTE: UnitCommitment.jl v0.4.2's validator under-reports the power balance
# whenever load shedding is used. validate.jl wraps a single-scenario solution
# as Dict("s1" => solution) at line 32, then guards the curtailment term with
# `"Load curtail (MW)" in keys(solution)` at line 569 -- which now tests the
# wrapped dict, whose only key is "s1". The term is therefore always zero and
# every optimal solution that sheds load is reported as unbalanced. The check
# below is the same power balance with curtailment actually included.
function independent_balance_check(instance, solution; tol = 1e-3)
    sc = instance.scenarios[1]
    worst, worst_t = 0.0, 0
    for t in 1:instance.time
        load = sum(b.load[t] for b in sc.buses; init = 0.0)
        curtail = sum(
            solution["Load curtail (MW)"][b.name][t] for b in sc.buses; init = 0.0
        )
        prod = sum(
            solution["Thermal production (MW)"][g.name][t] for
            g in sc.thermal_units; init = 0.0
        )
        prod += sum(
            solution["Profiled production (MW)"][p.name][t] for
            p in sc.profiled_units; init = 0.0
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
        residual = load - curtail - prod + charge - discharge
        if abs(residual) > abs(worst)
            worst, worst_t = residual, t
        end
    end
    return abs(worst) <= tol, worst, worst_t
end

balanced, worst, worst_t = independent_balance_check(instance, solution)
@printf("independent power balance: %s (max residual %.6f MW at t=%d)\n",
        balanced ? "OK" : "VIOLATED", worst, worst_t)

println("\nsolution sections: ", join(sort(collect(keys(solution))), ", "))

committed = sum(count(x -> x > 0.5, v) for (_, v) in solution["Is on"]; init = 0)
starts = sum(count(x -> x > 0.5, v) for (_, v) in solution["Switch on"]; init = 0)
stops = sum(count(x -> x > 0.5, v) for (_, v) in solution["Switch off"]; init = 0)
@printf("unit-hours committed: %d\n", committed)
@printf("startups / shutdowns: %d / %d\n", starts, stops)

shed = sum(sum(v) for (_, v) in solution["Load curtail (MW)"]; init = 0.0)
thermal = sum(sum(v) for (_, v) in solution["Thermal production (MW)"]; init = 0.0)
profiled = sum(sum(v) for (_, v) in solution["Profiled production (MW)"]; init = 0.0)
demand = sum(sum(b.load) for b in instance.scenarios[1].buses; init = 0.0)
@printf("demand:               %.0f MWh\n", demand)
@printf("thermal production:   %.0f MWh\n", thermal)
@printf("profiled production:  %.0f MWh\n", profiled)
@printf("load shed:            %.0f MWh (%.2f%% of demand)\n",
        shed, 100 * shed / demand)

exit(balanced ? 0 : 1)
