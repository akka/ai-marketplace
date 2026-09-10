# Releasing

## Public release

1. decide the appropriate version
2. trigger the [version-bump](https://github.com/akka/ai-marketplace/actions/workflows/version-bump.yml) workflow to create a PR
3. approve and merge that PR
4. use the shell block shown in the PR to create the GH release **and
   advance the `stable` tag** to point at the released commit

Step 4 is what customers on the default `--channel stable` see. The
`stable` tag is a floating pointer maintained by this repo; moving it is
what puts a new release of the marketplace assets in front of every
customer's next `akka specify init`. The CLI mechanism that consumes it
is documented in [cli/docs/specify-staging-channels.md](https://github.com/akka/akka/blob/main/cli/docs/specify-staging-channels.md).

The stable-channel constitution comes from
`https://doc.akka.io/_attachments/constitution.md` — the docs-site
publish pipeline is the release gate for that file. `akka-sdk` does
**not** need a `stable` tag; the CLI only reads its `main` branch when a
caller opts into `--channel edge`.

### The `stable` tag contract

- Always points at the tip of `main` at the moment of a release cut.
- Advanced with `git tag -f stable <sha> && git push -f origin refs/tags/stable`.
  This is one of two places in the repo where a force-push is permitted;
  it is expected for this tag by design.
- To roll back a bad release, re-advance `stable` to the previous release
  commit. Every subsequent `akka specify init` picks up the rollback
  immediately; no CLI upgrade required.

### Pre-release / internal validation

There is no separate `next` branch. Internal contributors and CI use
`--channel edge`, which resolves to `main` for this repo (and to `main`
of `akka-sdk` for the constitution). That is how a change gets
exercised end-to-end before it becomes part of a release; `main` is
where velocity lives, `stable` is where customers live.

If a change must reach customers immediately without waiting for the
scheduled release, cut a release from the current `main` tip and advance
`stable` as above.

## Related

- CLI mechanism that consumes `stable`: [cli/docs/specify-staging-channels.md](https://github.com/akka/akka/blob/main/cli/docs/specify-staging-channels.md).
