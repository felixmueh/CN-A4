use crate::{Graph, GraphAdjacencyList};
use rand::Rng;

#[derive(Debug)]
pub struct SISGraph<'a> {
    graph: &'a GraphAdjacencyList,
    infected1: Vec<bool>,
    infected2: Vec<bool>,
    first_is_current: bool,
    n_infected: usize,

    // much quicker to just keep track of the number of infected neighbors
    n_infected_neighbors: Vec<usize>,
    recovery_rate: f64,
    infection_rate: f64,
    rng: rand::rngs::ThreadRng,
}

impl<'a> SISGraph<'a> {
    pub fn n_infected(&self) -> usize {
        self.n_infected
    }

    pub fn n_nodes(&self) -> usize {
        self.graph.n_nodes()
    }

    pub fn prop_infected(&self) -> f64 {
        self.n_infected as f64 / self.graph.n_nodes() as f64
    }

    pub fn reset(&mut self, infection_rate: f64, recovery_rate: f64) {
        self.recovery_rate = recovery_rate;
        self.infection_rate = infection_rate;
        self.n_infected = 0;
        for i in 0..self.graph.n_nodes() {
            self.infected1[i] = self.rng.gen::<f64>() < 0.2;
            if self.infected1[i] {
                self.n_infected += 1;
            }
            self.n_infected_neighbors[i] = 0;
        }

        for i in 0..self.graph.n_nodes() {
            if self.infected1[i] {
                for j in self.graph.nodes[i].iter() {
                    self.n_infected_neighbors[*j] += 1;
                }
            }
        }
        self.first_is_current = true;
    }

    pub fn from_graph(
        graph: &'a GraphAdjacencyList,
        recovery_rate: f64,
        infection_rate: f64,
    ) -> Self {
        let n_nodes = graph.n_nodes();
        let infected1 = vec![true; n_nodes];
        let infected2 = vec![true; n_nodes];
        let n_infected_neighbors = vec![0; n_nodes];

        let rng = rand::thread_rng();

        let mut g = Self {
            graph,
            infected1,
            infected2,
            first_is_current: true,
            n_infected_neighbors,
            n_infected: n_nodes,
            recovery_rate,
            infection_rate,
            rng,
        };
        g.reset(infection_rate, recovery_rate);
        g
    }

    pub fn step(&mut self) {
        let (infected, infected_next) = if self.first_is_current {
            (&mut self.infected1, &mut self.infected2)
        } else {
            (&mut self.infected2, &mut self.infected1)
        };

        for i in 0..self.graph.n_nodes() {
            infected_next[i] = infected[i];
            if infected[i] {
                if self.rng.gen::<f64>() < self.recovery_rate {
                    infected_next[i] = false;
                }
            } else {
                let n_infected_neighbors = self.n_infected_neighbors[i];
                // TODO: Check this formula
                if self.rng.gen::<f64>()
                    > (1.0 - self.infection_rate).powf(n_infected_neighbors as f64)
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
                self.n_infected += 1;
            } else if !infected_next[i] && infected[i] {
                for j in self.graph.nodes[i].iter() {
                    self.n_infected_neighbors[*j] -= 1;
                }
                self.n_infected -= 1;
            }
        }
        debug_assert!(self.n_infected == infected_next.iter().filter(|&&x| x).count());
        self.first_is_current = !self.first_is_current;
    }
}
