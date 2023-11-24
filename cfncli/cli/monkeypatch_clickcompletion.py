from click import MultiCommand
from click_completion.core import resolve_ctx, match, Option, Argument, \
    completion_configuration


def get_choices(cli, prog_name, args, incomplete):
    """

    Parameters
    ----------
    cli : click.Command
        The main click Command of the program
    prog_name : str
        The program name on the command line
    args : [str]
        The arguments already written by the user on the command line
    incomplete : str
        The partial argument to complete

    Returns
    -------
    [(str, str)]
        A list of completion results. The first element of each tuple is actually the argument to complete, the second
        element is an help string for this argument.
    """
    ctx = resolve_ctx(cli, prog_name, args)
    if ctx is None:
        return
    optctx = None
    if args:
        options = [param
                   for param in ctx.command.get_params(ctx)
                   if isinstance(param, Option)]
        arguments = [param
                     for param in ctx.command.get_params(ctx)
                     if isinstance(param, Argument)]
        for param in options:
            if not param.is_flag and args[-1] in param.opts + param.secondary_opts:
                optctx = param
        if optctx is None:
            for param in arguments:
                if (
                        not incomplete.startswith("-")
                        and (
                        ctx.params.get(param.name) in (None, ())
                        or param.nargs == -1
                )
                ):
                    optctx = param
                    break
    choices = []
    if optctx:
        choices += [c if isinstance(c, tuple) else (c, None) for c in
                    optctx.type.complete(ctx, incomplete)]
        if not choices and hasattr(optctx,
                                   'autocompletion') and optctx.autocompletion is not None:
            dynamic_completions = optctx.autocompletion(ctx=ctx, args=args,
                                                        incomplete=incomplete)
            choices += [c if isinstance(c, tuple) else (c, None) for c in
                        dynamic_completions]
    else:
        for param in ctx.command.get_params(ctx):
            if (
                    completion_configuration.complete_options or incomplete and not incomplete[
                                                                                    :1].isalnum()) and isinstance(
                    param, Option):
                # filter hidden click.Option
                if getattr(param, 'hidden', False):
                    continue
                for opt in param.opts:
                    if match(opt, incomplete):
                        choices.append((opt, param.help))
                for opt in param.secondary_opts:
                    if match(opt, incomplete):
                        # don't put the doc so fish won't group the primary and
                        # and secondary options
                        choices.append((opt, None))
        if isinstance(ctx.command, MultiCommand):
            for name in ctx.command.list_commands(ctx):
                if match(name, incomplete):
                    choices.append(
                        (name, ctx.command.get_command_short_help(ctx, name)))

    for item, help in choices:
        yield (item, help)


def monkey_patch():
    import click_completion
    click_completion.core.get_choices = get_choices
