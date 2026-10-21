import sys
sys.path.insert(0, "/tmp/delegation-swarm-main/host-run/workspaces/swarm-reducer-1819251bb1")
from totals import aggregate, total
print("aggregate([]):", aggregate([]), "sum([]):", sum([]))
print("aggregate([7]):", aggregate([7]), "sum([7]):", sum([7]))
print("aggregate([2,3]):", aggregate([2,3]), "sum([2,3]):", sum([2,3]))
print("total(\"2,3\"):", total("2,3"), "expected:", 5)
