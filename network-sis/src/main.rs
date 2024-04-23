use std::fs::File;

use sis_sim::GraphEdgeList;
use sis_sim::SISGraph;

fn main() {
    let mut file = File::open("../WS_graph_1000_10_0.2.net").unwrap();
    let G = GraphEdgeList::read_pajek(&mut file).unwrap();
    let G = SISGraph::from_graph(G.into(), 0.1, 0.1);

    println!("{:?}", G);
}
