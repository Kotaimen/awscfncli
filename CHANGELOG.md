# Changelog

## V3

### Version 3.0.0 (2020-05-02)

Features:
- Added backoff to `sync` command when CloudFormation API is throttled (contributed by KotMeow).

### Version 3.0.0b1 (2020-02-19)

Issues:

- Use monkey patching for dynamic auto complete as PyPi don't allow use git as upper stream package.
- Add 1.x unitests back. 

### Version 3.0.0b0 (2020-02-18)

Features:

- Drop support for Python2.7.
- Switch dev environment to pipenv.
- Be more forgiven with package dependency.
- Refactored `cli` package.
- Minor change to cli command & options.
- Command line auto complete support. 

## V2

### Version 2.1.19 (2019-10-24)

Issues:
- Add disable-tail-events option to stack sync command, workaround for throttling 
  during concurrent deployment. (Contributed by KotMeow).  

### Version 2.1.18 (2019-9-2)
Issues
- Don't use semantic_version for parsing config version, fixes 
  compatibly issue.

### Version 2.1.17 (2019-7-20)

Issues:
- Fix `pyyaml` version conflict with `awscli`. 

### Version 2.1.16 (2019-7-20)

Issues:
- Relax `pyyaml` version limit. 

### Version 2.1.15 (2019-6-27)

Issues:
- Relax `jsonschema` version limit. 
  
### Version 2.1.14 (2019-6-7)

Issues:
- Made ppt.confirm return the results from click.confirm. (contributed by 
  Andrew Lytle)

### Version 2.1.13 (2019-6-6)

Issues:
- Changed sync to not abort if a single Change Set is declined. (contributed by 
  Andrew Lytle)
  
### Version 2.1.12 (2019-5-31)

Issues:
- Fix deployment error in samples caused nodejs 6 lambda runtime is EOL.
  
### Version 2.1.11 (2019-5-31)

Issues:
- Disable custom packed resources to keep template compatiable with awscfncli
  and samcli.

### Version 2.1.10 (2019-5-1)

Issues:
- Fixes package error after awscli `1.16.145`

### Version 2.1.9 (2019-3-14)

Hotfix

### Version 2.1.8 (2019-3-14)

Issues:
- Refactor cross stack reference, and fixed Python 2.7 bug. 

### Version 2.1.7 (2019-3-1)

Features:
- Add change details to pretty print of ChangeSets (contributed by Andy)

### Version 2.1.6 (2019-2-17)

Issues:
- Fix Python 3.6 compatibility issue introduced in `2.1.5`.

### Version 2.1.5 (2019-2-9)

Issues:
- Fix compatibility problem with string.Template

### Version 2.1.4 (2019-1-23)

Issues:
- Fix release issue

### Version 2.1.3 (2019-1-23)

Issues:
- Fix json dump error caused by template contains complex types (datetime objects).

### Version 2.1.2 (2019-1-13)

Issues:
- Fix failure when string template returns None as match object.
- supports CAPABILITY_AUTO_EXPAND

### Version 2.1.1 (2019-1-4)

Issues:
- Fix issue caused by awcli > 1.16.77
- Fix issue that a plain '$' will accidentally match the cross stack reference patten

Features:
- Print changeset execution note before actually calling boto3
- Colorize changeset replacement so user get alarmed when resource replacement happens


### Version 2.1.0 (2018-12-08)

Features:
- Support Cross Stack Reference in config version 3
- Refactor stack command and config

### Version 2.0.5 (2018-11-30)

Issues:
- Check template existence before package
- Enable setting arifactory store in command line

### Version 2.0.4 (2018-10-26)

Issues:
- Fix compatibility issue for awscli > 1.16.23

### Version 2.0.3 (2018-10-23)

Issues:
- Fix package_data definition.

### Version 2.0.2 (2018-10-23)

Issues:
- Fix awscli import error.

### Version 2.0.1 (2018-08-17)

Issues:
- Fix missing package files, update related tests.

### Version 2.0.0 (2018-05-1)

Issues:
- Override doesn't work properly when blueprint doesn't contain a parameter section
- Allow creating and applying ChangeSets when stack is in REVIEW_IN_PROGRESS status
- Allow "_" in stack and stage names

### Version 2.0.0-rc2 (2018-05-1)

Issues:
- Fix distribution conflict with old version of awscfncli


### Version 2.0.0-rc1 (2018-05-1)

Rewrite and incompatible with previous version.

Features:
- New CLI interface
- Multi-stages and stacks in a single config file
- Supports SAM and new `sync` command to easy SAM deployment
- Additional custom packaging resources

Deferred Features:
- `changeset` command
- Environment variable support in config file
- Specify deployment order


## V1

### Version 0.5.2 (2018-04-17)

Features:
- Add command for setting termination protection

Issues:
- Return error when exception raised. Fix #17

### Version 0.5.1 (2017-10-11)

Features:
- Add cost command to estimate cost of templates

Issues:
- Fix import error for awscli version later than 1.11.161

### Version 0.5 (2017-07-21)

Features:
- Add command for template packaging.


### Version 0.4 (2017-07-13)

Features:
- Package referenced resources before deploying the template.
- Support deploying template with specified service role.

### Version 0.3.4 (2017-05-12)

Issues:
- Fix unittest error.


### Version 0.3.3 (2017-05-12)

Issues:
- Fix incorrect canned stack policies.

### Version 0.3.2 (2017-04-25)

Features:
- Add "--execute" option to changeset create subcommand.

### Version 0.3.1 (2017-01-24)

Issues:
- Fix Exception when describe a change set with resource change type is "Remove".

### Version 0.3 (2017-01-23)

Features:
- Improve subcommand help.
- Add `template reflect` sub command which generated

Issues:
- Fix bug that `template validate` fails when `TemplateBody` is used.

### Version 0.2 (2017-01-19)

Features:
- Improve stack and ChangeSet description command output format.
- Add the ability to display stack export/import values.
- Remove `--detail` option from stack describe subcommand.
- Add `--stack-resources` option to stack describe subcommand.
- Add `--stack-exports` option to stack describe subcommand.

Issues:
- Fix bug that TemplateBody failed to load template file.

### Version 0.1.2 (2017-01-17)

Chore:
- Update keywords and description for SEO.

### Version 0.1.1 (2017-01-16)

Issues:
- Fix conflict release version.

### Version 0.1 (2017-01-16)

Features:
- Stack commands
- Template commands
- ChangeSet commands
- Test and coverage
