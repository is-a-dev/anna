![banner](https://embed.pixiv.net/spotlight.php?id=10119&lang=en)
# Anna
Anna is named after Anna Yanami from Makeine: Too Many Losing Heroines.
She is a fork of [orangcc](https://github.com/is-a-dev/orangcapp) meant to be a replacement for [Fire](https://github.com/is-a-dev/fire) and [orangcc](https://github.com/is-a-dev/orangcapp) in the is-a.dev Discord server.
What we've done so far:

- Merged Fire and orangcc together into a bot that functions as both
- Rewrote the Github module
- Rewrote the dns module
- Remove a lot of bloat from mostly orangcc's code
- Rewrote various commands
- Add some new modules, including the `purge` and `send` commands

**Branches**: `anna` is the stable branch while `komari` is the unstable development branch.

## todo
- [ ] make the tags reworked module work
- [ ] fix bugs with and rewrite bits of the help system; and make the tag prefix ^
- [ ] maybe remove the helpban system, why the hells does it exist if nobody uses it + we don't even need a bot for it when we can just use roles
- [ ] overall polish up the bot, add various utility modules and commands and things
- [ ] rewrite faq, suggestions, and something else i forgot shikanoko nokonoko koshitantan
- [ ] fix the various bugs and try to follow best practices where possible
- [ ] long term goal — rewrite both fire and orangcc code
- [ ] add a module that replaces the countr bot

## installation
On NixOS, run `nix run github:cutedog5695/anna`.

On Ubuntu/Debian: Soon

Maintainers: [@orxngc, @cutedog5695]