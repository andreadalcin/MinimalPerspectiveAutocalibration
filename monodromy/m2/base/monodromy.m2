restart
needsPackage "MonodromySolver"
needs "config.m2"

------------------------------------------------------------------------------------------
-- 0. Constants + Functions
nsq = x -> (ret := (transpose x * x); assert(numcols ret == 1 and numrows ret == 1); ret_(0,0))
contains = (i, L) -> (ret := not position(L, j -> i == j) === null);
normalizeDepths = method()
normalizeDepths Matrix := solution -> (
    depths := solution_{0..numcols solution -2};
    ret := 1/depths_(0,0) * depths | matrix{{solution_(0,numcols solution-1)}};
    ret
    )
normalizeDepths List := solution -> normalizeDepths matrix{solution}

eps = 1e-6
one = inputGate(1_CC)
zer0 = inputGate(0_CC)
vars(fxi, fyi, cx, cy, s)

------------------------------------------------------------------------------------------
-- 1. Encode a substitution for intrinsic parameters
params = sort delete(symbol one, delete(symbol zer0, unique values E))
nparams = length params
-- n_points depends on the n_params
npoints = if nparams <= 1 then 4 else if nparams <= 4 then 5 else 6

------------------------------------------------------------------------------------------
-- 2. Build synthetic scene (offline)
setRandomSeed("2023-06-13");
pfx = random CC
pfy = random CC
pcx = random CC
pcy = random CC
ps = random CC

-- Substitution rules: focal length
pfx = if E#(symbol fxi) === symbol one then 1_CC else pfx
pfy = if E#(symbol fyi) === symbol one then 1_CC else pfy
pfy = if E#(symbol fyi) === symbol fxi then pfx else pfy
-- Substitution rules: principal point
pcx = if E#(symbol cx) === symbol zer0 then 0_CC else pcx
pcy = if E#(symbol cy) === symbol zer0 then 0_CC else pcy
-- Substitution rules: skew
ps = if E#(symbol s) === symbol zer0 then 0_CC else ps

pfxi = 1_CC / pfx
pfyi = 1_CC / pfy
K = matrix {{pfx,ps,pcx},{0,pfy,pcy},{0,0,1}}
worldPoints = random(CC^3,CC^npoints)
worldPoints = worldPoints * inverse matrix for i from 1 to npoints list for j from 1 to npoints list if i==j then worldPoints_(2,0) else 0
xDepths = (K * worldPoints)^{2}
xPoints = (K * worldPoints) * inverse diagonalMatrix xDepths
translation1 = random(CC^3,CC^1)
rotation1 = (Atemp=random(CC^3,CC^3); S=Atemp-transpose Atemp; (id_(CC^3)-S)*inverse(id_(CC^3)+S))
worldPointsSecondFrame = rotation1*worldPoints + matrix{toList(npoints:translation1)}
yDepths = (K * worldPointsSecondFrame)^{2}
yPoints = (K * worldPointsSecondFrame) * inverse diagonalMatrix yDepths
translation2 = random(CC^3,CC^1)
rotation2 = (A = random(CC^3,CC^3); S = A-transpose A; (id_(CC^3)-S) * inverse(id_(CC^3)+S))
worldPointsThirdFrame = rotation2*worldPoints + matrix{toList(npoints:translation2)}
zDepths = (K * worldPointsThirdFrame)^{2}
zPoints = (K * worldPointsThirdFrame) * inverse diagonalMatrix zDepths

depths = normalizeDepths(xDepths | yDepths | zDepths)
pointMatrix = depths_{1..(numcols depths - 1)}
pointMatrix = if contains(symbol s, params) then matrix ps | pointMatrix else pointMatrix
pointMatrix = if contains(symbol fyi, params) then matrix pfyi | pointMatrix else pointMatrix
pointMatrix = if contains(symbol fxi, params) then matrix pfxi | pointMatrix else pointMatrix
pointMatrix = if contains(symbol cy, params) then matrix pcy | pointMatrix else pointMatrix
pointMatrix = if contains(symbol cx, params) then matrix pcx | pointMatrix else pointMatrix

x0 = point(pointMatrix)
z0 = point(matrix{(flatten entries xPoints^{0,1}) | (flatten entries yPoints^{0,1}) | (flatten entries zPoints^{0,1})})


------------------------------------------------------------------------------------------
-- 3. Build synthetic scene (online)
setRandomSeed("2023-06-13");
qfx = abs random RR
qfy = abs random RR
qcx = random RR
qcy = random RR
qs = random RR

-- Substitution rules: focal length
qfx = if E#(symbol fxi) === symbol one then 1_RR else qfx
qfy = if E#(symbol fyi) === symbol one then 1_RR else qfy
qfy = if E#(symbol fyi) === symbol fxi then qfx else qfy
-- Substitution rules: principal point
qcx = if E#(symbol cx) === symbol zer0 then 0_RR else qcx
qcy = if E#(symbol cy) === symbol zer0 then 0_RR else qcy
-- Substitution rules: skew
qs = if E#(symbol s) === symbol zer0 then 0_RR else qs

qfxi = 1_RR / qfx
qfyi = 1_RR / qfy
K = matrix {{qfx,qs,qcx},{0,qfy,qcy},{0,0,1}}
worldPoints = random(RR^3,RR^npoints)
worldPoints = worldPoints * inverse matrix for i from 1 to npoints list for j from 1 to npoints list if i==j then worldPoints_(2,0) else 0
xDepths = (K * worldPoints)^{2}
xPoints = (K * worldPoints) * inverse diagonalMatrix xDepths
translation1 = random(RR^3,RR^1)
rotation1 = (Atemp=random(RR^3,RR^3); S=Atemp-transpose Atemp; (id_(RR^3)-S)*inverse(id_(RR^3)+S))
worldPointsSecondFrame = rotation1*worldPoints + matrix{toList(npoints:translation1)}
yDepths = (K * worldPointsSecondFrame)^{2}
yPoints = (K * worldPointsSecondFrame) * inverse diagonalMatrix yDepths
translation2 = random(RR^3,RR^1)
rotation2 = (A = random(RR^3,RR^3); S = A-transpose A; (id_(RR^3)-S) * inverse(id_(RR^3)+S))
worldPointsThirdFrame = rotation2*worldPoints + matrix{toList(npoints:translation2)}
zDepths = (K * worldPointsThirdFrame)^{2}
zPoints = (K * worldPointsThirdFrame) * inverse diagonalMatrix zDepths

depths = normalizeDepths(xDepths | yDepths | zDepths)
pointMatrix = depths_{1..(numcols depths - 1)}
pointMatrix = if contains(symbol s, params) then matrix qs | pointMatrix else pointMatrix
pointMatrix = if contains(symbol fyi, params) then matrix qfyi | pointMatrix else pointMatrix
pointMatrix = if contains(symbol fxi, params) then matrix qfxi | pointMatrix else pointMatrix
pointMatrix = if contains(symbol cy, params) then matrix qcy | pointMatrix else pointMatrix
pointMatrix = if contains(symbol cx, params) then matrix qcx | pointMatrix else pointMatrix

qx0 = point(pointMatrix)
qz0 = point(matrix{(flatten entries xPoints^{0,1}) | (flatten entries yPoints^{0,1}) | (flatten entries zPoints^{0,1})})


------------------------------------------------------------------------------------------
-- 3. Build equations
parameterMatrix=gateMatrix{vars(
     	-- 1st image coordinates
     	flatten toList apply(1..2, i -> toList apply(1..npoints, j -> x_(i,j))) |
     	-- 2nd image coordinates
     	flatten toList apply(1..2, i -> toList apply(1..npoints, j -> y_(i,j))) |
     	-- 3rd image coordinates
     	flatten toList apply(1..2, i -> toList apply(1..npoints, j -> z_(i,j)))
	)};
unknownMatrix = gateMatrix{vars(
    	-- Intrinsic parameters
        apply(params, i -> value i) |
    	-- 1st view projective depths
    	flatten toList apply(2..npoints, i -> a_i) |
    	-- 2nd view projective depths
    	flatten toList apply(1..npoints, i -> b_i) |
    	-- 3rd view projective depths
    	flatten toList apply(1..npoints, i -> c_i)
	)};

xPointsSymbolic = matrix for i from 1 to 3 list for j from 1 to npoints list if i==3 then one else x_(i,j);
yPointsSymbolic = matrix for i from 1 to 3 list for j from 1 to npoints list if i==3 then one else y_(i,j);
zPointsSymbolic = matrix for i from 1 to 3 list for j from 1 to npoints list if i==3 then one else z_(i,j);

symsub = (sym) -> (ret := value E#sym)
efxi = value E#(symbol fxi)
efyi = value E#(symbol fyi)
ecx = value E#(symbol cx)
ecy = value E#(symbol cy)
es = value E#(symbol s)

invKSymbolic = matrix {{efxi, -es * efxi * efyi, -ecx * efxi + ecy * es * efxi * efyi}, {0,efyi,-ecy * efyi}, {0,0,1}};

xPointsWorldSymbolic = compress(invKSymbolic * xPointsSymbolic * matrix apply(npoints,i->apply(npoints,j->if i==j then if i==0 then one else a_(i+1) else zer0)));
yPointsWorldSymbolic = compress(invKSymbolic * yPointsSymbolic * matrix apply(npoints,i->apply(npoints,j->if i==j then b_(i+1) else zer0)));
zPointsWorldSymbolic = compress(invKSymbolic * zPointsSymbolic * matrix apply(npoints,i->apply(npoints,j->if i==j then c_(i+1) else zer0)));

neqs = 2 * length sort(subsets(npoints,2))

eqsXY = apply(sort(subsets(npoints,2)), S->((i,j) := (first sort S, last sort S); nsq(yPointsWorldSymbolic_{i} - yPointsWorldSymbolic_{j}) - nsq(xPointsWorldSymbolic_{i} - xPointsWorldSymbolic_{j})));
eqsXZ = apply(sort(subsets(npoints,2)), S->((i,j) := (first sort S, last sort S); nsq(zPointsWorldSymbolic_{i} - zPointsWorldSymbolic_{j}) - nsq(xPointsWorldSymbolic_{i} - xPointsWorldSymbolic_{j})));
eqs = eqsXY | eqsXZ;                	    	        -- set of all equations

-- Sanity check
GS = gateSystem(parameterMatrix, unknownMatrix, transpose gateMatrix{eqs});
assert areEqual(0,norm evaluate(GS, z0, x0));
J = evaluateJacobian(GS, z0, x0);
print(first SVD evaluateJacobian(GS, z0, x0));

------------------------------------------------------------------------------------------
-- 4. Test all possible combinations for non-singular Jacobian, write results to file
FOUT = "monodromy.csv" << ""
FOUT << "idx,n_complex,n_real" << endl

func = (i,R) -> (
    -- 1. Build GateSystem
    eqsMap = new MutableHashTable;
    for i from 0 to (length eqs - 1) do if contains(i,R) then eqsMap#i = eqs#i;
    GS = gateSystem(parameterMatrix, unknownMatrix, transpose gateMatrix{values eqsMap});
    print(R);

    -- 2. (offline): Run monodromy
    setDefault(tStepMin=>1e-8);
    setDefault(maxCorrSteps=>2);
    (V, npaths) = monodromySolve(GS, z0, {x0}, Verbose=>true, NumberOfNodes=>2, NumberOfEdges=>3, BatchSize=>100);
    print("monodromySolve: done!");
    print(length V.PartialSols);
    H = parametricSegmentHomotopy GS;
    startParameters = V.BasePoint;
    startSolutions = points V.PartialSols;

    -- 3. (online): Solve random instance using parameter homotopy
    targetParameters = qz0;
    combinedParameters = matrix startParameters | matrix targetParameters;
    H01 = specialize(H, transpose combinedParameters);
    targetSolutions = trackHomotopy(H01, startSolutions);
    realSolutions = realPoints targetSolutions;
    print(length realSolutions);

    -- 4. Look for the correct solution (within margin of error)
    validSolutions = for i from 0 to length(realSolutions)-1 list matrix realSolutions#i;
    gt = matrix { qx0#Coordinates };
    residuals = for i from 0 to length(validSolutions)-1 list norm(validSolutions#i - gt);
    print(min residuals);

    FOUT << (i) << "," << (length V.PartialSols) << "," << (length realSolutions)
)

for i from 0 to length C - 1 do func(i,C#i)

FOUT << close;
-- exit()
