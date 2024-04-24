use std::fs::File;
use std::io::Write;

use sis_sim::GraphEdgeList;
use sis_sim::SISGraph;

fn main() {
    let n_beta = 51;
    let beta_min = 0.0;
    let beta_max = 1.0;

    let args: Vec<String> = std::env::args().collect();
    let in_file = &args[1];
    let out_file = &args[2];
    let mu = args[3].parse::<f64>().unwrap();

    let mut file = File::open(in_file).expect("Failed to open file");
    // TODO: check components (should be one)
    let g = GraphEdgeList::read_pajek(&mut file).unwrap().into();

    let eps = 1e-10;
    let max_sim = 10000;
    let mut g = SISGraph::from_graph(&g, 0.0, 0.0);

    let mut results = Vec::new();
    for i in 0..n_beta {
        let beta = beta_min + (beta_max - beta_min) * (i as f64) / (n_beta as f64);
        g.reset(beta, mu);

        let mut prev = g.prop_infected();
        for i in 0.. {
            if i >= max_sim {
                panic!("Max sim reached");
            }
            g.step();
            let prop = g.prop_infected();
            if (prop - prev).abs() < eps {
                println!(
                    "Converged in {} steps to {}, for mu={}, beta={}",
                    i, prop, mu, beta
                );
                break;
            }
            prev = prop;
        }
        results.push((beta, g.prop_infected()));
    }
    let mut file = File::create(out_file).expect("Failed to create file");
    for (beta, prop) in results {
        writeln!(file, "{},{}", beta, prop).unwrap();
    }
}
