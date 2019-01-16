# Changelog

## Version 2.1.2 (2019-1-13)

Issues:
- Fix failure when string template returns None as match object.
- supports CAPABILITY_AUTO_EXPAND

## Version 2.1.1 (2019-1-4)

Issues:
- Fix issue caused by awcli > 1.16.77
- Fix issue that a plain '$' will accidentally match the cross stack reference patten

Features:
- Print changeset execution note before actually calling boto3
- Colorize changeset replacement so user get alarmed when resource replacement happens


## Version 2.1.0 (2018-12-08)

Features:
- Support Cross Stack Reference in config version 3
- Refactor stack command and config

## Version 2.0.5 (2018-11-30)

Issues:
- Check template existence before package
- Enable setting arifactory store in command line

## Version 2.0.4 (2018-10-26)

Issues:
- Fix compatibility issue for awscli > 1.16.23

## Version 2.0.3 (2018-10-23)

Issues:
- Fix package_data definition.

## Version 2.0.2 (2018-10-23)

Issues:
- Fix awscli import error.

## Version 2.0.1 (2018-08-17)

Issues:
- Fix missing package files, update related tests.

## Version 2.0.0 (2018-05-1)

Issues:
- Override doesn't work properly when blueprint doesn't contain a parameter section
- Allow creating and applying ChangeSets when stack is in REVIEW_IN_PROGRESS status
- Allow "_" in stack and stage names

## Version 2.0.0-rc2 (2018-05-1)

Issues:
- Fix distribution conflict with old version of awscfncli


## Version 2.0.0-rc1 (2018-05-1)

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


## Version 0.5.2 (2018-04-17)

Features:
- Add command for setting termination protection

Issues:
- Return error when exception raised. Fix #17


## Version 0.5.1 (2017-10-11)

Features:
- Add cost command to estimate cost of templates

Issues:
- Fix import error for awscli version later than 1.11.161


## Version 0.5 (2017-07-21)

Features:
- Add command for template packaging.


## Version 0.4 (2017-07-13)

Features:
- Package referenced resources before deploying the template.
- Support deploying template with specified service role.


## Version 0.3.4 (2017-05-12)

Issues:
- Fix unittest error.


## Version 0.3.3 (2017-05-12)

Issues:
- Fix incorrect canned stack policies.


## Version 0.3.2 (2017-04-25)

Features:
- Add "--execute" option to changeset create subcommand.


## Version 0.3.1 (2017-01-24)

Issues:
- Fix Exception when describe a change set with resource change type is "Remove".


## Version 0.3 (2017-01-23)

Features:
- Improve subcommand help.
- Add `template reflect` sub command which generated

Issues:
- Fix bug that `template validate` fails when `TemplateBody` is used.

## Version 0.2 (2017-01-19)

Features:
- Improve stack and ChangeSet description command output format.
- Add the ability to display stack export/import values.
- Remove `--detail` option from stack describe subcommand.
- Add `--stack-resources` option to stack describe subcommand.
- Add `--stack-exports` option to stack describe subcommand.

Issues:
- Fix bug that TemplateBody failed to load template file.


## Version 0.1.2 (2017-01-17)

Chore:
- Update keywords and description for SEO.


## Version 0.1.1 (2017-01-16)

Issues:
- Fix conflict release version.


## Version 0.1 (2017-01-16)

Features:
- Stack commands
- Template commands
- ChangeSet commands
- Test and coverage
