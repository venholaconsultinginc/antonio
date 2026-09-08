# Contributing

Thanks for considering it. Everything gets reviewed before it lands in `main`.

Two things shape what belongs here. First, antonio is seed code rather than a library: the scripts
exist to be read, copied and adapted, so a change that makes one shorter and clearer usually helps
more than one that makes it do more; capability you don't need is just something else to read
past. Second, the example databases are fabricated, and they're built elsewhere. No real person,
device or activity appears in any of them, and they arrive here signed and checksummed, so please
don't regenerate or hand-edit the `.sqlite` files in `example-data/`. A pull request that does
won't be merged, and the signature wouldn't verify afterwards anyway.

## Reporting a bug or asking for something

Use [the issue forms](https://github.com/venholaconsultinginc/antonio/issues/new/choose). They ask
for the few things that make a report actionable, and the bug form covers Cordelia and Kent as well
as antonio itself.

Everything you write in an issue is public the moment you submit it. No GitHub account, or
something you'd rather not post in the open? Email <help@venholaconsulting.ca> instead.

## Contributing code

1. Fork the repository and branch from `main`.
2. Make your change.
3. Open a pull request describing what it does and why.

Small, focused pull requests get reviewed faster than large ones. If you're planning something
substantial, open an issue first; that's the cheapest point at which to find out it's out of scope.

Web edits require a sign-off on the commit, and GitHub prompts for it automatically.

### What to check before opening a pull request

- Run the script you changed, against the bundled example database for its sport. Every script
  runs with no arguments and takes `--db` to point at a database of your own.
- Regenerate anything derived. The sport pages in `docs/` quote real script output, the summary
  metrics block and the strength-training exercise table, so if your change alters what a script
  prints, update the page to match.
- Plots too. If a plot changes, regenerate the copy in `docs/` as well as the one under
  `reports/output/` (which isn't committed).
- Keep to the standard library plus what's already in `requirements.txt`. A new dependency costs
  something to everyone reading a script in order to copy it, so it needs a reason.
- Match the surrounding style. These scripts are documentation as much as code, and comments here
  explain *why* something is done, particularly where the FIT format or Cordelia's schema is
  surprising.

## Documentation

Documentation changes are as welcome as code. The pages under `docs/` are written for someone who
knows Python but has never seen a Cordelia database, so if something there wasn't clear to you,
that's worth an issue or a pull request on its own, with no code attached.

Documentation is English-only.

## Licensing

The code and documentation are MIT licensed; the SVG illustrations are dedicated to the public
domain under CC0 1.0. By contributing you agree your contribution ships under those same terms.
