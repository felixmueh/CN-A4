use std::fs::File;

use sis_sim::GraphEdgeList;
use sis_sim::SISGraph;

fn main() {
    let mut file = File::open("../WS_graph_1000_10_0.2.net").unwrap();
    let G = GraphEdgeList::read_pajek(&mut file).unwrap();
    let mut G = SISGraph::from_graph(G.into(), 0.1, 0.1);

    let eps = 1e-10;
    let max_sim = 10000;
    let mut prev = G.prop_infected();
    for i in 0.. {
        if i >= max_sim {
            panic!("Max sim reached");
        }
        G.step();
        let prop = G.prop_infected();
        if (prop - prev).abs() < eps {
            println!("Converged in {} steps to {}", i, prop);
            break;
        }
        prev = prop;
    }
}
