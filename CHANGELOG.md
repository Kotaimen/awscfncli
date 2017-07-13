# Changelog

## Version 0.4.0 (2017-07-13)

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
