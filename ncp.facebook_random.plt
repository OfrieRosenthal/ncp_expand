#
# Graph: ./datasets/facebook/facebook_random.edgelist -> facebook_random facebook_random. A=0.001, K=1000-1.5-100M, Cvr=10, SzFrc=0.001 G(4035, 96230) (Sun Sep 14 17:33:08 2025)
#

set title "Graph: ./datasets/facebook/facebook_random.edgelist -> facebook_random facebook_random. A=0.001, K=1000-1.5-100M, Cvr=10, SzFrc=0.001 G(4035, 96230)"
set key bottom right
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel "k (number of nodes in the cluster)"
set ylabel "{/Symbol \F} (conductance)"
set tics scale 2
set terminal png font arial 10 size 1000,800
set output 'ncp.facebook_random.png'
plot 	"ncp.facebook_random.tab" using 1:2 title "ORIGINAL MIN (4035, 96230)" with lines lw 1
