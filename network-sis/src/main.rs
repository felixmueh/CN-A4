use std::fs::File;

use network_gen::GraphEdgeList;

fn main() {
    let mut file = File::open("../WS_graph_1000_10_0.2.net").unwrap();
    let G = GraphEdgeList::read_pajek(&mut file).unwrap();
    println!("{:?}", G);
}
