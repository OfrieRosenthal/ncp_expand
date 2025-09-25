#
# Graph: ../facebook_combined.txt -> facebook_combined facebook_combined. A=0.001, K=1000-1.5-100M, Cvr=10, SzFrc=0.001 G(3698, 85963) (Thu Sep 25 17:28:31 2025)
#

set title "Graph: ../facebook_combined.txt -> facebook_combined facebook_combined. A=0.001, K=1000-1.5-100M, Cvr=10, SzFrc=0.001 G(3698, 85963)"
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
set output 'ncp.facebook_combined.png'
plot 	"ncp.facebook_combined.tab" using 1:2 title "ORIGINAL MIN (3698, 85963)" with lines lw 1
