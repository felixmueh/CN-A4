use std::fs::File;
use std::io::Write;

use sis_sim::GraphEdgeList;
use sis_sim::SISGraph;

const VERBOSE: bool = false;

fn main() {
    let n_beta = 51;
    let beta_min = 0.0;
    let beta_max = 1.0;

    let args: Vec<String> = std::env::args().collect();
    let in_file = &args[1];
    let out_file = &args[2];
    let mu = args[3].parse::<f64>().unwrap();

    let mut file = File::open(in_file).expect(format!("Failed to open file {}", in_file).as_str());
    // TODO: check components (should be one)
    let g = GraphEdgeList::read_pajek(&mut file).unwrap().into();

    // this eps is for an early stop when convergence
    let eps = 0.001;
    // maximume allowed occilation if not converged
    let eps_panic = 0.10;
    let max_sim = 5000;
    let mut cnt_no_change = 0;
    let cnt_required = 3;
    let mut g = SISGraph::from_graph(&g, 0.0, 0.0);

    let mut results = Vec::new();
    for i in 0..n_beta {
        let beta = beta_min + (beta_max - beta_min) * (i as f64) / (n_beta as f64);
        g.reset(beta, mu);

        let mut prev = g.prop_infected();
        for i in 0.. {
            g.step();
            let prop = g.prop_infected();
            let delta = (prop - prev).abs();
            if i >= max_sim {
                if delta > eps_panic {
                    panic!(
                        "Max sim reached and not converged for {}, mu={}, delta={}",
                        in_file,
                        mu,
                        (prop - prev).abs()
                    );
                }
                break;
            }
            if (prop - prev).abs() < eps {
                cnt_no_change += 1;
            } else {
                cnt_no_change = 0;
            }
            if cnt_no_change >= cnt_required {
                if VERBOSE {
                    println!(
                        "Converged in {} steps to {}, for mu={}, beta={}",
                        i, prop, mu, beta
                    );
                }
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
