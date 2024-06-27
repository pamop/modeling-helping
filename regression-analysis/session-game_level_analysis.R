# FINAL ANALYSIS
# Session and Game level
# We tried a lot of things and ultimately this is the important stuff.

library(lme4)
library(lmtest)

##########################################
# Data
##########################################
# set working directory to where this repo is located
setwd("~/Documents/gureckis lab/modeling-helping")

# import data
# subject level demographics
demographic_data = read.csv('data/demographic_data.csv')

# game data
seshdf <- read.csv("data/sessiondf.csv")
subjseshdf <- read.csv("data/subjsessiondf.csv")
gamedf <- read.csv("data/gamedf.csv")
subjgamedf <- read.csv("data/subjgamedf.csv")
trialdf <- read.csv("data/trialdf.csv")
envfeats <- read.csv("data/environment_features.csv")

# Set unordered variables as factors
# SESSION LEVEL FACTORS
seshdf <- within(seshdf, {
  session <- factor(session)
  costCond <- factor(costCond)
  resourceCond <- factor(resourceCond)
  visibilityCond <- factor(visibilityCond)
  counterbalance <- factor(counterbalance)
  helped <- factor(helped)
  redHelped <- factor(redHelped)
  purpleHelped <- factor(purpleHelped)
})

# WITHIN-SUBJECT BETWEEN-SESSION LEVEL FACTORS
subjseshdf <- within(subjseshdf, {
  session <- factor(session)
  costCond <- factor(costCond)
  resourceCond <- factor(resourceCond)
  visibilityCond <- factor(visibilityCond)
  counterbalance <- factor(counterbalance)
  subjid <- factor(subjid) # new  
  agent <- factor(agent) # new
  helped <- factor(helped)
  partnerHelped <- factor(partnerHelped)
})

# GAME LEVEL FACTORS
gamedf <- within(gamedf, {
  session <- factor(session)
  costCond <- factor(costCond)
  resourceCond <- factor(resourceCond)
  visibilityCond <- factor(visibilityCond)
  counterbalance <- factor(counterbalance)
  objectLayer <- factor(objectLayer) # changes between games in a sesh
  redFirst <- factor(redFirst) # changes between games in a sesh
  environment <- factor(environment)
  patchUniformity <- factor(patchUniformity)
  helped <- factor(helped)
  redHelped <- factor(redHelped)
  purpleHelped <- factor(purpleHelped)
})

# WITHIN-SUBJECT BETWEEN-GAME LEVEL FACTORS
subjgamedf <- within(subjgamedf, {
  session <- factor(session)
  costCond <- factor(costCond)
  resourceCond <- factor(resourceCond)
  visibilityCond <- factor(visibilityCond)
  counterbalance <- factor(counterbalance)
  objectLayer <- factor(objectLayer)
  redFirst <- factor(redFirst)
  subjid <- factor(subjid) # specifies subject identity  
  meFirst <- factor(meFirst) # changes between games in a sesh (now, relevant to subj identity) 
  agent <- factor(agent) # specifies subject identity
  patchUniformity <- factor(patchUniformity) # feature of the environment of the game
  environment <- factor(environment)
  helped <- factor(helped)
  redHelped <- factor(redHelped)
  purpleHelped <- factor(purpleHelped)
  partner_helped_thisgame <- factor(partner_helped_thisgame)
  player_helped_lastgame <- factor(player_helped_lastgame)
  partner_helped_lastgame <- factor(partner_helped_lastgame)
})

# TRIAL LEVEL FACTORS
trialdf <- within(trialdf, {
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

##########################################
# Regressions on performance
##########################################

d<-subjgamedf # trying with this df instead
summary(d)

# starting from the null model, build up regressions with parameters of interest

# null model
mp0 <- lm(points~1,data=d)

# simplest (minimal) fixed effects only model
mp1 <- lm(points ~ gameNum + objectLayer + costCond 
          + resourceCond + visibilityCond + meFirst + agent + ownBPsize,
          data=d)

# simplest mixed (random intercepts)
mp2 <- lmer(points ~ gameNum + objectLayer + costCond 
            + resourceCond + visibilityCond + meFirst + agent + ownBPsize 
            + (1|subjid),
            data=d)

# compare these three models
t(AIC(mp0,mp1,mp2)) # mp2 has lowest AIC
lrtest(mp2,mp1,mp0) # likelihood ratio test suggests additional parameters in mp2 substantially improve the fit

# Instead of using environment number as a parameter, let's use features of environment
# each environment is unique but the twelve envs share various features

# fixed effects only, environment features only
mp3 <- lm(points ~ gameNum + costCond + resourceCond + visibilityCond
          + meFirst + agent + ownBPsize  + nOwnVeg + nOtherVeg + patchUniformity,
          data=d)

# mixed (random intercepts) environment features only
mp4 <- lmer(points ~ gameNum + costCond + resourceCond + visibilityCond
            + meFirst + agent + ownBPsize  + nOwnVeg + nOtherVeg + patchUniformity
            + (1|subjid),
            data=d)

# Compare prev models with new ones using environment features instead of identity
lrtest(mp4,mp3,mp2,mp1,mp0) # indeed mp4 has better fit than previous models

# Now we want to see if helping features improve the model
# Since we're predicting performance we can use players helping on this game as a parameter
# (helping_event and helpful_steps) which we don't use in the helping regressions since
# in those, the current player helping is what we are trying to predict

# fixed only, env feats and helping feats
mp5 <- lm(points ~ gameNum + costCond + resourceCond + visibilityCond
          + meFirst + agent + ownBPsize  + nOwnVeg + nOtherVeg + patchUniformity
          + partner_helpingevents_lastgame + partner_helpingevents_thisgame
          + partner_helpfulsteps_lastgame + partner_helpfulsteps_thisgame
          + player_helpingevents_lastgame + player_helpfulsteps_lastgame
          + helping_event + helpful_steps,
          data=d)

# mixed, env feats and helping feats
mp6 <- lmer(points ~ gameNum + costCond + resourceCond + visibilityCond
            + meFirst + agent + ownBPsize  + nOwnVeg + nOtherVeg + patchUniformity
            + partner_helpingevents_lastgame + partner_helpingevents_thisgame
            + partner_helpfulsteps_lastgame + partner_helpfulsteps_thisgame
            + player_helpingevents_lastgame + player_helpfulsteps_lastgame
            + helping_event + helpful_steps
            + (1|subjid),
            data=d)
# To compare 3 and 4 to 5 and 6, have to restrict to just the subset of data
# with non-null helping data
mp3b <- lm(points ~ gameNum + costCond + resourceCond + visibilityCond
           + meFirst + agent + ownBPsize  + nOwnVeg + nOtherVeg + patchUniformity,
           subset=!is.na(partner_helpingevents_lastgame),
           data=d)
mp4b <- lmer(points ~ gameNum + costCond + resourceCond + visibilityCond
             + meFirst + agent + ownBPsize  + nOwnVeg + nOtherVeg + patchUniformity
             + (1|subjid),
             subset=!is.na(partner_helpingevents_lastgame),
             data=d)

# so compare mp4 with mp5 and 6 (must use subset of data due to missing values)
t(AIC(mp3b,mp4b,mp5,mp6)) # mp6 lowest AIC score
lrtest(mp6,mp5,mp4b,mp3b) # likelihood ratio test suggests mp6 fit is improved with the addnl params
# likelihood ratio test suggests additional parameters in mp6 substantially improve the fit

# Stats for displaying model results
mp6summary<-summary(mp6)
mp6coefs <- coef(mp6summary)
# 95% confidence intervals on the estimates
mp6cis <- stats::confint(mp6,parm=names(fixef(mp6))) # takes several seconds to run
mp6cis <- cbind(mp6coefs[,"Estimate"],mp6cis)
# ANOVA for DFs, F-vals and p(>F)
mp6anova <- anova(mp6)

# Took these and formatted them in excel then converted to latex
mp6summary
mp6cis
mp6anova

##########################################
# Regressions on helping
##########################################

# Session level (one observation per subject)
# Null model
m0 <- glm(helped ~ 1, 
          data=subjseshdf, 
          family="binomial")
# minimal session-level model
m1 <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize,
          data=subjseshdf, 
          family="binomial")
# adding helping feature
m2 <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
          + partnerHelpingEvents,
          data=subjseshdf, 
          family="binomial")
# adding additional helping feature
m3 <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
           + partnerHelpingEvents + partnerHelpfulSteps,
           data=subjseshdf,
           family="binomial")
t(AIC(m0,m1,m2,m3)) # m2 is best, so helpfulsteps feature doesnt seem to help
lrtest(m0,m1,m2,m3) # can also do these lr tests pairwise to see that m2 wins

# Format m2 for presentation of results
m2summary <- summary(m2)
m2_cis <- stats::confint(m2) # 95% confidence intervals
m2_coefs <- cbind(coef(m2summary), OddsRatio=exp(coef(m2))) # compute odds ratio of estimates

# Game level (12 observations per subject)
# Now we can include environment details as predictors

# Null model
m0b <- glm(helped ~ 1, 
          data=subjgamedf, 
          family="binomial")
# minimal session-level model
m1b <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize,
          data=subjgamedf, 
          family="binomial")
# adding helping feature
m2b <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
          + partnerHelpingEvents,
          data=subjgamedf, 
          family="binomial")
# minimal fixed effects only, with environment by identity not features
m3 <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
          + gameNum + objectLayer + meFirst,
          data=subjgamedf,
          family=binomial)
# minimal fixed effects only, with environment by features
m4 <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
          + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity,
          data=subjgamedf,
          family=binomial)
lrtest(m4,m3) # m4 is better
# fixed with env features and helping events of current (partner only) and previous game
m5 <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
          + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity
          + partner_helpingevents_lastgame + partner_helpingevents_thisgame
          + player_helpingevents_lastgame,
          data=subjgamedf,
          family=binomial)
m4b <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
           + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity,
           data=subjgamedf,
           subset=!is.na(partner_helpingevents_lastgame),
           family=binomial)
lrtest(m5,m4b) # m5 is better

# fixed with env features and helping events and helpful steps of current (partner only) and previous game
m6 <- glm(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
          + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity
          + partner_helpingevents_lastgame + partner_helpingevents_thisgame
          + player_helpingevents_lastgame + partner_helpfulsteps_lastgame
          + partner_helpfulsteps_thisgame + player_helpfulsteps_lastgame,
          data=subjgamedf,
          family=binomial)
lrtest(m6,m5) # m6 is better

# in another file i tested all of the minimal models with subject level intercepts and 
# adding the subj level intercepts always improved the fit
# the mixed models take a while to run so i'm not replicating all of them here
# just a few interesting variations

# minimal model with mixed effects (subj intercepts)
m7 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
            + gameNum + objectLayer + meFirst + (1|subjid),
            data=subjgamedf,
            family=binomial,
            control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))
# environment by features not arbitrary name
m8 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
            + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity
            + (1|subjid),
            data=subjgamedf,
            family=binomial,
            control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))
lrtest(m8,m7) # m8 is better, so we use environment features not labels

# adding helping
# helping events 
m9 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
             + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity
             + partner_helpingevents_lastgame + partner_helpingevents_thisgame
             + player_helpingevents_lastgame
             + (1|subjid),
             data=subjgamedf,
             family=binomial,
             control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))
m8b <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
            + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity
            + (1|subjid),
            data=subjgamedf,
            subset=!is.na(partner_helpingevents_lastgame),
            family=binomial,
            control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))
lrtest(m9,m8b) # m9 better
# helping events AND helpful steps
m10 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
             + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity
             + partner_helpingevents_lastgame + partner_helpingevents_thisgame
             + player_helpingevents_lastgame + partner_helpfulsteps_lastgame
             + partner_helpfulsteps_thisgame + player_helpfulsteps_lastgame
             + (1|subjid),
             data=subjgamedf,
             family=binomial,
             control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))
lrtest(m10,m9) # m10 better
# add session level intercepts. i don't anticipate these making a big difference
m11 <- glmer(helped ~ costCond + visibilityCond + resourceCond + agent + ownBPsize
             + gameNum + meFirst + nOwnVeg + nOtherVeg + patchUniformity
             + partner_helpingevents_lastgame + partner_helpingevents_thisgame
             + player_helpingevents_lastgame + partner_helpfulsteps_lastgame
             + partner_helpfulsteps_thisgame + player_helpfulsteps_lastgame
             + (1|subjid) + (1|session),
             data=subjgamedf,
             family=binomial,
             control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))
lrtest(m11,m10) # as expected, adding the session level intercepts doesn't improve the fit

# let's confirm that model 10 also wins against the equivalent model without mixed effects
lrtest(m10,m6)
t(AIC(m10,m6))

# In conclusion model 10 wins
# Let's format it for presenting the results
# I want to show the estimates with stats from model fit, and add confidence intervals and odds ratios
m10summary <- summary(m10)
m10coefs <- coef(m10summary)
OddsRatio <- exp(m10coefs[,"Estimate"])
m10coefs <- cbind(m10coefs, OddsRatio)
m10coefs <- cbind(m10coefs, confint(m10, parm= c(rownames(m10coefs)),method="Wald"))
col_order <- c("Estimate", "2.5 %", "97.5 %", "Std. Error", "z value", "Pr(>|z|)", "OddsRatio") 
m10coefs <- m10coefs[,col_order]
m10_formatted <- format(round(m10coefs, 2), nsmall = 2)
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
sig <- getsigcolumn(m10coefs)
m10_formatted <- cbind(m10_formatted, sig)

m10_formatted

