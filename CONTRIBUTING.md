# Contributing

Thanks for considering it. Contributions are welcome, and every one of them gets reviewed before
it lands — there is no path into `main` that skips that.

Two things worth knowing before you start, because they shape what belongs here:

- **antonio is seed code, not a library.** The scripts exist to be read, copied and adapted. A
  change that makes a script shorter and clearer is usually more valuable here than one that makes
  it more capable, because capability you don't need is just something else to read past.
- **The example databases are fabricated, and they are built elsewhere.** No real person, device or
  activity is represented in any of them. They arrive here signed and checksummed, so please don't
  regenerate or hand-edit the `.sqlite` files in `example-data/` — a pull request that does won't be
  merged, and the signature would no longer verify anyway.

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
substantial, open an issue first and we'll talk about it before you spend the time — it's the
cheapest point to find out that something is out of scope.

Web edits require a sign-off on the commit; GitHub prompts for it automatically.

### What to check before opening a pull request

- **Run the script you changed**, against the bundled example database for its sport. Every script
  runs with no arguments and takes `--db` to point at a database of your own.
- **Regenerate anything derived.** The sport pages in `docs/` quote real script output — the
  summary metrics block, and the strength-training exercise table. If your change alters what a
  script prints, update the page to match, or the two drift apart silently.
- **Plots too.** If a plot changes, the copy in `docs/` needs regenerating, not just the one under
  `reports/output/` (which isn't committed).
- **Keep it stdlib plus what's already in `requirements.txt`.** New dependencies are a real cost to
  someone reading a script to copy it, so they need a reason.
- **Match the surrounding style.** These scripts are documentation as much as code; comments explain
  *why* something is done, particularly where the FIT format or Cordelia's schema is surprising.

## Documentation

Documentation changes are as welcome as code. The pages under `docs/` are written for someone who
knows Python but has never seen a Cordelia database — if something there wasn't clear to you, that's
worth an issue or a pull request on its own, and it doesn't need code attached.

Documentation is English-only.

## Licensing

The code and documentation are MIT licensed; the SVG illustrations are dedicated to the public
domain under CC0 1.0. By contributing you agree your contribution ships under those same terms.
