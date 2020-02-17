# V3 Wish List

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
