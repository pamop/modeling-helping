# trial level analyses
library(lme4)
library(lmtest)

##########################################
# Data
##########################################
# import data
setwd("~/Documents/gureckis lab/modeling-helping")

# subject level demographics
demographic_data = read.csv('data/demographic_data.csv')

# game data
df <- read.csv("data/trialdf.csv") # takes a few sec to load
envfeats <- read.csv("data/environment_features.csv")

# Set unordered variables as factors
# TRIAL LEVEL FACTORS
df <- within(df, {
  session <- factor(session)
  costCond <- factor(costCond)
  resourceCond <- factor(resourceCond)
  visibilityCond <- factor(visibilityCond)
  counterbalance <- factor(counterbalance)
  objectLayer <- factor(objectLayer)
  redFirst <- factor(redFirst)
  subjid <- factor(subjid)
  meFirst <- factor(meFirst)
  agent <- factor(agent)
  eventName <- factor(eventName) # changes within a game
  target <- factor(target) # changes within a game
  gameover <- factor(gameover) # changes within a game
  lastTrial <- factor(lastTrial) # changes within a game
  targetColor <- factor(targetColor) # changes within a game
  targetCat <- factor(targetCat) # changes within a game
  actionCat <- factor(actionCat) # changes within a game
  helped <- factor(helped)
  player_helped_lasttrial <- factor(player_helped_lasttrial)
  partner_helped_lasttrial <- factor(partner_helped_lasttrial)
})

# drop the trials where gameover==True because these are not real "turns"
# just indicators of the state at "the end of the game round
trialdf <- df[df$gameover=="False",]

# tons of descriptive columns but we may not use them all
summary(trialdf)

# Trial level
m0 <- glm(helped ~ 1, 
           data=trialdf, 
           family="binomial")

mfull <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent 
               + gameNum + turnCount
               + ownBPsize + otherBPsize
               + nOwnVegFarm + nOtherVegFarm + nOwnVegBox + nOtherVegBox
               + nOwnVegInOwnBP + nOtherVegInOwnBP + nOwnVegInOtherBP + nOtherVegInOtherBP
               + ownScore + otherScore + ownPointsCumulative + otherPointsCumulative
               + ownEnergy + otherEnergy
               + ownDistanceToClosestOwnVeg + ownDistanceToClosestOtherVeg
               + otherDistanceToClosestOwnVeg + otherDistanceToClosestOtherVeg
               + partner_helpingevents_lasttrial + partner_helpfulsteps_lasttrial
               + player_helpingevents_lasttrial + player_helpfulsteps_lasttrial
               + ownHelpingEventsToDate + otherHelpingEventsToDate
               + ownHelpfulStepsToDate + otherHelpingStepsToDate
               + (1|subjid),
             data=trialdf,
             family=binomial,
             control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=1e6)))
mfullsummary<-summary(mfull)
mfullsummary
# fixed-effect model matrix is rank deficient so dropping 3 columns / coefficients
# Warning messages:
# 1: Some predictor variables are on very different scales: consider rescaling 
# 2: In checkConv(attr(opt, "derivs"), opt$par, ctrl = control$checkConv,  :
#    Model failed to converge with max|grad| = 15.0552 (tol = 0.002, component 1)
# 3: In checkConv(attr(opt, "derivs"), opt$par, ctrl = control$checkConv,  :
#    Model is nearly unidentifiable: very large eigenvalue
#    - Rescale variables?;
#    Model is nearly unidentifiable: large eigenvalue ratio
#   - Rescale variables?

# trying to address warnings using the following guide: https://rstudio-pubs-static.s3.amazonaws.com/33653_57fc7b8e5d484c909b615d8633c01d51.html

# Taken from Kate Nussenbaum
#scale function
scale_this <- function(x){
  (x - mean(x, na.rm=TRUE)) / sd(x, na.rm=TRUE)
}

# rescale and center continuous vars
summary(trialdf)
dfs <- trialdf
# just the reg relevant columns not every numerical column in the df
numericalCols <- list("gameNum","turnCount","ownBPsize","otherBPsize",
                      "nOwnVegFarm","nOtherVegFarm","nOwnVegBox","nOtherVegBox",
                      "nOwnVegInOwnBP","nOtherVegInOwnBP","nOwnVegInOtherBP","nOtherVegInOtherBP",
                      "ownScore","otherScore","ownPointsCumulative","otherPointsCumulative","ownEnergy","otherEnergy",
                      "ownDistanceToClosestOwnVeg","ownDistanceToClosestOtherVeg",
                      "otherDistanceToClosestOwnVeg","otherDistanceToClosestOtherVeg",
                      "partner_helpingevents_lasttrial","partner_helpfulsteps_lasttrial",
                      "player_helpingevents_lasttrial","player_helpfulsteps_lasttrial",
                      "ownHelpingEventsToDate","otherHelpingEventsToDate",
                      "ownHelpfulStepsToDate","otherHelpingStepsToDate")
for (x in numericalCols){
  dfs[,x] <- scale_this(dfs[,x])
}
summary(dfs)
mfull_scaled <- update(mfull, data = dfs) # start from last attempt

# if needed:
# # check singularity - any of the random effects theta params very close to zero? < 10e-6
# tt <- getME(mfull_scaled,"theta")
# ll <- getME(mfull_scaled,"lower")
# min(tt[ll==0])
# 
# 
# # try starting again from last fit, maybe with more iterations
# ss <- getME(mfull_scaled,c("theta","fixef"))
# m2 <- update(mfull_scaled,start=ss,
#              control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))


# look at converged model results
mfullsummary <- summary(mfull_scaled)
mfullsummary
mfullcoefs <- coef(mfullsummary)
OddsRatio <- exp(mfullcoefs[,"Estimate"])
mfullcoefs <- cbind(mfullcoefs, OddsRatio)
mfullcoefs <- cbind(mfullcoefs, confint(mfull, parm= c(rownames(mfullcoefs)),method="Wald"))
col_order <- c("Estimate", "2.5 %", "97.5 %", "Std. Error", "z value", "Pr(>|z|)", "OddsRatio") 
mfullcoefs <- mfullcoefs[,col_order]
# mfull_formatted <- format(round(mfullcoefs, 2), nsmall = 2)
mfullcoefs
# cute lil function if you wanna add the asterisks like the model summaries do
getsigcolumn <- function(m){
  sig <- list()
  for (p in m[,'Pr(>|z|)']){
    if (p<0.001){
      sig <- append(sig,"***")
    } else if (p<0.01){
      sig <- append(sig,"**")
    } else if (p<0.05){
      sig <- append(sig,"*")
    } else if (p<0.1){
      sig <- append(sig,".")
    }else{
      sig <- append(sig," ")
    }
  }
  return(sig)
}
sig <- getsigcolumn(mfullcoefs)
mfullcoefs <- cbind(mfullcoefs, sig)

mfull2 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent 
               + gameNum + turnCount
               + ownBPsize
               + partner_helpingevents_lasttrial
               + (1|subjid),
               data=dfs, #scaled
               family=binomial,
               control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=1e6)))
               
mfull3 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent 
                + gameNum + turnCount 
                + ownBPsize
                + ownEnergy
                + ownDistanceToClosestOtherVeg
                + partner_helpingevents_lasttrial
                + (1|subjid),
                data=dfs, #scaled
                family=binomial,
                control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=1e6)))

mfull4 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent 
                + gameNum + turnCount
                + ownBPsize
                + ownEnergy
                + ownDistanceToClosestOtherVeg
                + partner_helpingevents_lasttrial
                + otherHelpingEventsToDate
                + (1|subjid),
                data=dfs, #scaled
                family=binomial,
                control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=1e6)))              
# look at converged model results
mfull4summary <- summary(mfull4)
mfull4summary
mfull4coefs <- coef(mfull4summary)
OddsRatio <- exp(mfull4coefs[,"Estimate"])
mfull4coefs <- cbind(mfull4coefs, OddsRatio)
mfull4coefs <- cbind(mfull4coefs, confint(mfull4, parm= c(rownames(mfull4coefs)),method="Wald"))
col_order <- c("Estimate", "2.5 %", "97.5 %", "Std. Error", "z value", "Pr(>|z|)", "OddsRatio") 
mfull4coefs <- mfull4coefs[,col_order]
# mfull_formatted <- format(round(mfullcoefs, 2), nsmall = 2)
sig <- getsigcolumn(mfull4coefs)
mfull4coefs <- cbind(mfull4coefs, sig)
mfull4coefs

# we could add a group effect of session, but it is a little redundant with ID
mfull5 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent 
                + gameNum + turnCount
                + ownBPsize
                + ownEnergy
                + ownDistanceToClosestOtherVeg
                + partner_helpingevents_lasttrial
                + otherHelpingEventsToDate
                + (1|session)
                + (1|subjid),
                data=dfs, #scaled
                family=binomial,
                control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=1e6)))              
# look at converged model results
mfull5summary <- summary(mfull5)
mfull5summary
mfull5coefs <- coef(mfull5summary)
OddsRatio <- exp(mfull5coefs[,"Estimate"])
mfull5coefs <- cbind(mfull5coefs, OddsRatio)
mfull5coefs <- cbind(mfull5coefs, confint(mfull5, parm= c(rownames(mfull5coefs)),method="Wald"))
col_order <- c("Estimate", "2.5 %", "97.5 %", "Std. Error", "z value", "Pr(>|z|)", "OddsRatio") 
mfull5coefs <- mfull5coefs[,col_order]
# mfull_formatted <- format(round(mfullcoefs, 2), nsmall = 2)
sig <- getsigcolumn(mfull5coefs)
mfull5coefs <- cbind(mfull5coefs, sig)
mfull5coefs

lrtest(mfull4,mfull5) #,mfull3,mfull2,mfull)
t(AIC(mfull5,mfull4))
