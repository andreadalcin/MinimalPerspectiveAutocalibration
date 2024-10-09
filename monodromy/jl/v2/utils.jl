# function nsq(x)
#     transpose(x) * x
# end

function subsets(x, y)
    collect(combinations(1:x,y))
end

function rand_rot()
    tmp = rand(3,3)
    S = tmp - transpose(tmp)
    return (Matrix{ComplexF64}(I, 3, 3) - S) * inv(Matrix{ComplexF64}(I, 3, 3) + S)
end

function normalizeDepths(solution)
    depths = solution[1:(size(solution)[1] - 1)]
    depths = vcat(1 / depths[1] * depths, solution[size(solution)[1]])
end

function myshowall(io, x, limit = false) 
    println(io, summary(x), ":")
    Base.print_matrix(IOContext(io, :limit => limit), x)
  end

function remove!(a, item)
    deleteat!(a, findall(x->x==item, a))
end