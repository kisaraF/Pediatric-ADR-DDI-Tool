library(openEBGM)
library(dplyr)

data <- read.csv('ebgm_prepared_data.csv')
View(data)

# clean data
df_clean <- data[data$E_ > 0 & is.finite(data$E_) & is.finite(data$N_), ]

# rename columns
data_t <- df_clean %>% rename(N=N_) %>% rename(E=E_)

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
  alpha1 = c(0.1, 0.05, 0.01),
  beta1  = c(0.1, 0.05, 0.01),
  alpha2 = c(1.0, 2.0, 0.5),
  beta2  = c(1.0, 2.0, 0.5),
  p      = c(0.1, 0.2, 0.05)
)

# bypass autoHyper and run the raw optimizer directly
raw_hypers <- exploreHypers(
  squashed_data, 
  theta_init = theta_init, 
  squashed = TRUE,
  max_pts = 100000
)
print(raw_hypers)

theta_hat <- c(
  alpha1 = 7.753965e-09,
  beta1  = 0.006937961,
  alpha2 = 0.5376849,
  beta2  = 0.3418686,
  p      = 0.1944204
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


