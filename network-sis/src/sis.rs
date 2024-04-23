use crate::{Graph, GraphAdjacencyList};
use rand::Rng;

#[derive(Debug)]
pub struct SISGraph {
    graph: GraphAdjacencyList,
    infected1: Vec<bool>,
    infected2: Vec<bool>,
    first_is_current: bool,

    // much quicker to just keep track of the number of infected neighbors
    n_infected_neighbors: Vec<usize>,
    recovery_rate: f64,
    infection_rate: f64,
    rng: rand::rngs::ThreadRng,
}

impl SISGraph {
    pub fn from_graph(graph: GraphAdjacencyList, recovery_rate: f64, infection_rate: f64) -> Self {
        let n_nodes = graph.n_nodes();
        let infected1 = vec![false; n_nodes];
        let infected2 = vec![false; n_nodes];
        let n_infected_neighbors = vec![0; n_nodes];
        let first_is_current = true;
        let rng = rand::thread_rng();

        Self {
            graph,
            infected1,
            infected2,
            first_is_current,
            n_infected_neighbors,
            recovery_rate,
            infection_rate,
            rng,
        }
    }

    pub fn step(&mut self) {
        let (infected, infected_next) = if self.first_is_current {
            (&mut self.infected1, &mut self.infected2)
        } else {
            (&mut self.infected2, &mut self.infected1)
        };

        for i in 0..self.graph.n_nodes() {
            if infected[i] {
                if self.rng.gen::<f64>() < self.recovery_rate {
                    infected_next[i] = false;
                }
            } else {
                let n_infected_neighbors = self.n_infected_neighbors[i];
                // TODO: Check this formula
                if self.rng.gen::<f64>()
                    < 1.0 - (1.0 - self.infection_rate).powf(n_infected_neighbors as f64)
                {
                    infected_next[i] = true;
                }
            }
        }

        for i in 0..self.graph.n_nodes() {
            if infected_next[i] && !infected[i] {
                for j in self.graph.nodes[i].iter() {
                    self.n_infected_neighbors[*j] += 1;
                }
            } else if !infected_next[i] && infected[i] {
                for j in self.graph.nodes[i].iter() {
                    self.n_infected_neighbors[*j] -= 1;
                }
            }
        }
    }
}
