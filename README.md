# AWS CloudFormation CLI

The missing AWS CloudFormation CLI.

## V3 Wish List

Functional features:

- [ ] Rigid configuration file check (don't allow unknown parameters).
- [ ] Environment variable substation in configuration.
- [ ] Cross stack reference supports other stack properties instead of outputs only
  - [ ] Now: `${StageName.StackName.OutputName}`
    New: `${StageName.StackName.Outputs.OutputName}`
     `${StageName.StackName.StackId}`
     `${AWS::Region}-foobarbaz`
    The old format still allowed
- [x] CLI auto complete
- [ ] Fix the termination protection config.
- [ ] Fix CloudForamtion API call throttling.
- [ ] New ChangeSets commands.
- [ ] Automatic deployment order discovery.
- [ ] Deploy stacks concurrently.

Non-functional:

- [X] Migrate local development/build to `pipenv`, with makefile based 
- [X] Use absolute import and restructure package imports.
- [x] Refractor cli package structure (use semi-dynamic subcommand load)
  - [ ] Try to move shared options/arguments to separate decorator functions
- [ ] Testing
  - [ ] int-test for cli commands
  - [ ] unittest for internal stuff
  - [ ] smoke testing for pre-release check
- [x] Drop support for py2.
- [ ] Drop support for v1 schema.
- [ ] Drop unnecessary 3rd party dependency.
- [ ] Cross stack reference fix (replace with real parser).
- [ ] Call `awscli` directly for packaging instead of use internal hack.

## Introduction

`awscfncli` helps build and manage AWS CloudFormation stacks. 

Features:

- Manage stacks in different accounts & regions in a single YAML config file.
- Organize stack using stages and blueprints. 
- Select stacks to operate on using globs.
- Cross-stack parameter reference.
- Automatically package and upload template resources.
- Push button SAM deployment using `stack sync` command.
- Display and tracking stack events in the CLI.
- List stack resources, outputs and exports in the CLI.

## Install

Install using [pip](https://pip.pypa.io/) from [pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli2

If you are install `cfn-cli` globally, using [`pipx`](https://github.com/pipxproject/pipx) is recommended:

    pipx install awscfncli2 

### Shell Auto Completion

Auto completion is supported by `click` and `click_completion`, supported shells are `bash`, `zsh` , `fish` and `Powershell`.  To install auto completion, run this in target shell:

```
> cfn-cli --install-completion
fish completion installed in /Users/Bob/.config/fish/completions/cfn-cli.fish
```

Three types of auto completions are supported:

- Commands and sub commands.
- Options and parameters.
- Dynamic complete for `--profile` and `--stacks`.

```
> cfn-cli drift d<TAB><TAB> 
detect  (Detect stack drifts.)  diff  (Show stack resource drifts.)

> cfn-cli stack deploy --<TAB> <TAB>
--disable-rollback  (Disable rollback if stack creation failed. You can specify ei…)
--help                                                 (Show this message and exit.)
--ignore-existing               (Don't exit with error if the stack already exists.)
--no-wait                                (Exit immediately after deploy is started.)
--on-failure  (Determines what action will be taken if stack creation fails. This …)
--timeout-in-minutes  (The amount of time in minutes that can pass before the stac…)

> cfn-cli stack deploy --on-failure <TAB> <TAB>
DELETE  DO_NOTHING  ROLLBACK

> cfn-cli -s <TAB><TAB>
Develop.ApiBackend-Develop           (ApiBackend-Develop)
Production.ApiBackend-Production  (ApiBackend-Production)
Staging.ApiBackend-Staging           (ApiBackend-Staging)
```

