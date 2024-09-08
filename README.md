![banner](https://embed.pixiv.net/spotlight.php?id=10119&lang=en)
# Anna
Anna is named after Anna Yanami from Makeine: Too Many Losing Heroines.
She is meant to be a replacement for Fire and orangcc in the is-a.dev Discord server.
What we've done so far:

- Merged Fire and orangcc together into a bot that functions as both
- Rewrite the Github module
- Rewrite the dns module
- Remove a lot of bloat from mostly orangcc's code and some from Fire's code as well
- Rewrite various commands
- Add some new modules, including the `purge` and `send` commands

**Branches**: `anna` is the stable branch while `komari` is the unstable development branch.

## todo
- [ ] make the tags reworked module work
- [ ] fix bugs with and rewrite bits of the help system; and make the tag prefix ^
- [ ] maybe remove the helpban system, why the hells does it exist if nobody uses it + we don't even need a bot for it when we can just use roles

## installation
On NixOS, run `nix run cutedog5695/anna`.