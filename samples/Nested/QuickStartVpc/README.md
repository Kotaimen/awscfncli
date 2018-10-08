Use nested stack as a "bridge" to convert stack output to stack Import/Export.

Replace EC2 key name with your in `cfn-cli.yml` then deploy.

Note this `EnableTerminationProtection` is enabled so you have to manually 
disable them in the config file or in console before delete the stacks.  
`cfn-cli` does _not_ support overwriting `EnableTerminationProtection` on
command line and this is by design.
  
