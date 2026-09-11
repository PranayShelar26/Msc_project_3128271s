# Cross-Architecture Energy Prediction for Scientific Workflow Tasks

MSc Dissertation — School of Computing Science, University of Glasgow
Author: Pranay Prakash Shelar

This repository contains the code used for this dissertation: data processing,
model training, cross-architecture and cross-vendor evaluation, and the
energy-aware scheduling simulation.

## Overview

Scientific workflows run many tasks across heterogeneous hardware, where the same
task can consume very different amounts of runtime, memory, and energy depending
on where it runs. Measuring every task on every machine does not scale. This work
instead builds a machine-learning model that **predicts a task's energy (and
runtime and memory)** from its characteristics and those of the target hardware,
studies **whether those predictions transfer to unseen hardware**, and uses them
to **schedule tasks to reduce energy consumption**.

The central finding is that the three targets differ in how strongly they depend
on hardware — **memory < runtime < energy** — and this ordering explains every
result: memory transfers across machines almost for free, runtime does not, and
energy is hardest of all. A small amount of target-architecture data, or a single
calibration factor, is enough to make predictions usable on new hardware without
full re-measurement.

The model is a Random Forest trained on a unified dataset of 22,672 tasks across
8 architectures, built from the Augur (energy) and Lotaru (runtime, memory)
profiling datasets.
