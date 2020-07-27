# Introduction
This app maps CSV files with django models
It tries to support above all the following cases:
- A simple mapping
  1. Simple mapping between a one-to-one correspondence.
     In other words, a file corresponds to a django model
  2. Simple mapping with one or more Foreingkeys associated to the model
  3. Pre_save and post_save methods

- How use
  1. Initialize with context
  2. Validate
  3. Save

- Deployment
  1. Install app
  2. Supervisor
