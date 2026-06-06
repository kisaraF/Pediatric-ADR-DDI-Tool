library(openEBGM)
library(dplyr)

data <- read.csv('ebgm_prepared_data.csv')
View(data)

# rename columns
data_t <- data %>% rename(N=total_pair_count) %>% rename(E=expected_pair_count)

# calculate the relative reporting ratio
data_t$rr <- data_t$N / data_t$E

# squash data
# groups pairs with similar expected counts to drastically speed up 
# the hyperparameter estimation without losing statistical fidelity.
squashed_data <- autoSquash(data_t)
View(squashed_data)

# define initial hyperparameters for the Multi-Gamma distribution
# These are standard starting points for FDA FAERS data
theta_init <- data.frame(
  alpha1 = c(0.2, 0.1, 0.5),
  beta1  = c(0.1, 0.1, 0.5),
  alpha2 = c(2.0, 10.0, 6.0),
  beta2  = c(4.0, 10.0, 6.0),
  p      = c(1/3, 0.2, 0.5)
)

# bypass autoHyper and run the raw optimizer directly
raw_hypers <- exploreHypers(
  squashed_data, 
  theta_init = theta_init, 
  squashed = TRUE, 
  max_pts = 100000
)

print(raw_hypers)

# since a successful convergence is found, the values 
# can be hard-coded to theta_hat
theta_hat <- c(
  alpha1 = 4.645852e-10,
  beta1  = 0.1647272,
  alpha2 = 1.992758,
  beta2  = 4.001966,
  p      = 0.4532660
)

# calculate the posterior mixture fractions (qn)
qn <- Qn(theta_hat, N = data_t$N, E = data_t$E)

# calculate the Empirical Bayes Geometric Mean (EBGM)
data_t$EBGM <- ebgm(theta_hat, N = data_t$N, E = data_t$E, qn = qn)

# calculate the lower 5th percentile bound (EB05) - key paper metric
data_t$EB05 <- quantBisect(
  percent = 5, 
  theta_hat = theta_hat, 
  N = data_t$N, 
  E = data_t$E, 
  qn = qn
)

# calculating the upper 95th percentile, optionally
data_t$EB95 <- quantBisect(
  percent = 95, 
  theta_hat = theta_hat, 
  N = data_t$N, 
  E = data_t$E, 
  qn = qn
)

# export
write.csv(data_t, "ebgm_computed.csv", row.names = FALSE)


