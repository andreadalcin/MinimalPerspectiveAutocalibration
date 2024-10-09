using HomotopyContinuation
using LinearAlgebra
using Combinatorics
using Random

include("config.jl");
include("utils.jl");


# ------------------------------------------------------------------------------------------
# 0. Constants + Functions
zer0 = ComplexF64(0)
one  = ComplexF64(1)


# ------------------------------------------------------------------------------------------
# 1. Encode a substitution for intrinsic parameters
params = sort(collect(values(E)))
remove!(params, Symbol("one"))
remove!(params, Symbol("zer0"))
nparams = length(params)
# n_points depends on the n_params
npoints = nparams <= 1 ? (4) : (nparams <= 4 ? 5 : 6)

@polyvar cx cy fxi fyi s a[2:npoints] b[1:npoints] c[1:npoints] x[1:2,1:npoints] y[1:2,1:npoints] z[1:2,1:npoints] l


# ------------------------------------------------------------------------------------------
# 2. Build synthetic scene
Random.seed!(2);
pfx = rand(ComplexF64)
pfy = rand(ComplexF64)
pcx = rand(ComplexF64)
pcy = rand(ComplexF64)
ps  = rand(ComplexF64)

# Substitution rules: focal length
pfx = E[Symbol("fxi")] == Symbol("one") ? one : pfx
pfy = E[Symbol("fyi")] == Symbol("one") ? one : pfy
pfy = E[Symbol("fyi")] == Symbol("fxi") ? pfx : pfy
# Substitution rules: principal point
pcx = E[Symbol("cx")] == Symbol("zer0") ? zer0 : pcx
pcy = E[Symbol("cy")] == Symbol("zer0") ? zer0 : pcy
# Substitution rules: skew
ps  = E[Symbol("s")] == Symbol("zer0") ? zer0 : ps

pfxi = one / pfx
pfyi = one / pfy

K = [pfx ps pcx
     0 pfy pcy
     0 0 1]

worldPoints = rand(ComplexF64, (3, npoints))
worldPoints = worldPoints * inv(diagm([worldPoints[3,1] for i in collect(1:npoints)]))
xDepths = (K * worldPoints)[3,:]
xPoints = (K * worldPoints) * inv(diagm(xDepths))

translation1 = rand(ComplexF64, (3,1))
rotation1 = rand_rot()
worldPointsSecondFrame = rotation1 * worldPoints + repeat(translation1, 1, npoints)
yDepths = (K * worldPointsSecondFrame)[3,:]
yPoints = (K * worldPointsSecondFrame) * inv(diagm(yDepths))

translation2 = rand(ComplexF64, (3,1))
rotation2 = rand_rot()
worldPointsThirdFrame = rotation2 * worldPoints + repeat(translation2, 1, npoints)
zDepths = (K * worldPointsThirdFrame)[3,:]
zPoints = (K * worldPointsThirdFrame) * inv(diagm(zDepths))

depths = normalizeDepths(vcat(xDepths, yDepths, zDepths))
pointMatrix = depths[2:size(depths)[1]]
pointMatrix = Symbol("s") in params   ? vcat(ps, pointMatrix) : pointMatrix
pointMatrix = Symbol("fyi") in params ? vcat(pfyi, pointMatrix) : pointMatrix
pointMatrix = Symbol("fxi") in params ? vcat(pfxi, pointMatrix) : pointMatrix
pointMatrix = Symbol("cy") in params  ? vcat(pcy, pointMatrix) : pointMatrix
pointMatrix = Symbol("cx") in params  ? vcat(pcx, pointMatrix) : pointMatrix

x0 = pointMatrix
z0 = vcat(xPoints[1:2,:][:], yPoints[1:2,:][:], zPoints[1:2,:][:])


# ------------------------------------------------------------------------------------------
# 3. Build equations
parameterMatrix = [
    # 1st image coordinates
    (x[1:2,1:npoints]...);
    # 2nd image coordinates
    (y[1:2,1:npoints]...);
    # 3rd image coordinates
    (z[1:2,1:npoints]...);
]
unknownMatrix = vcat(
    # Intrinsic parameters
    map(x -> eval(x), params),
    # 1st view projective depths
    (a[1:npoints-1]...), 
    # 2nd view projective depths
    (b[1:npoints]...), 
    # 3rd view projective depths
    (c[1:npoints]...) 
)

xPointsSymbolic = transpose([x[1,1:npoints] x[2,1:npoints] repeat([1], npoints)])
yPointsSymbolic = transpose([y[1,1:npoints] y[2,1:npoints] repeat([1], npoints)])
zPointsSymbolic = transpose([z[1,1:npoints] z[2,1:npoints] repeat([1], npoints)])

efx = eval(E[Symbol("fxi")])
efy = eval(E[Symbol("fyi")])
ecx = eval(E[Symbol("cx")])
ecy = eval(E[Symbol("cy")])
es  = eval(E[Symbol("s")])

invKSymbolic = transpose([[efx, -es * efx * efy, -ecx * efx + ecy * es * efx * efy] [0, efy, -ecy * efy] [0,0,1]])

xPointsWorldSymbolic = invKSymbolic * xPointsSymbolic * diagm([i > 1 ? a[i-1] : l for i in collect(1:npoints)])
xPointsWorldSymbolic = subs(xPointsWorldSymbolic, (l) => (1))
yPointsWorldSymbolic = invKSymbolic * yPointsSymbolic * diagm([b[i] for i in collect(1:npoints)])
zPointsWorldSymbolic = invKSymbolic * zPointsSymbolic * diagm([c[i] for i in collect(1:npoints)])

neqs = 2 * length(subsets(npoints,2))

eqsXY = [nsq(yPointsWorldSymbolic[:,i] - yPointsWorldSymbolic[:,j]) - nsq(xPointsWorldSymbolic[:,i] - xPointsWorldSymbolic[:,j]) for (i,j) in subsets(npoints,2)]
eqsXZ = [nsq(zPointsWorldSymbolic[:,i] - zPointsWorldSymbolic[:,j]) - nsq(xPointsWorldSymbolic[:,i] - xPointsWorldSymbolic[:,j]) for (i,j) in subsets(npoints,2)]
eqs   = vcat(eqsXY, eqsXZ)
@assert norm(subs(eqs, vcat(unknownMatrix, parameterMatrix) => vcat(x0, z0))) < 1e-8

function run_monodromy(config)
    println("Running monodromy for configuration:")
    println(config)

    eqs = vcat(eqsXY, eqsXZ)
    eqs = eqs[[c + 1 for c in config]]

    tracker_options = TrackerOptions(; automatic_differentiation = 3)
    res = monodromy_solve(eqs, x0, z0; parameters = parameterMatrix, tracker_options = tracker_options)
end

[run_monodromy(config) for config in graph_configs]

