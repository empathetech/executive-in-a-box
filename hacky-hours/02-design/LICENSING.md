# Licensing

<!-- Ask about licenses early — before dependencies are chosen.
     A dependency's license can constrain what license your product can use.
     Fill this in during Level 1 (Constraints & Values) and keep it updated. -->

## Chosen License

MIT License

## Rationale

This project exists to put power in the hands of workers. MIT is the most permissive common open source license — anyone can use, modify, fork, and build on this tool, including commercially. The tool itself stays free; what people build on top of it is their business.

MIT is compatible with virtually all other open source licenses, which matters because we'll be pulling in LLM SDKs, local storage libraries, and potentially MCP tooling from many sources.

## Dependency Compatibility

Update this table before adding any new dependency. If a dependency's license is incompatible or unclear, flag it before merging.

| Dependency | License | Compatible? | Notes |
|------------|---------|-------------|-------|
| (none yet) | —       | —           | Update as dependencies are added |

### Licenses to watch out for

- **GPL / AGPL**: requires your code to also be GPL if you distribute it. MIT code can use GPL libraries but the resulting work becomes GPL — check before adding.
- **Commons Clause** or **SSPL**: look like open source but restrict commercial use. Not compatible with MIT intent.
- **CC BY-NC**: non-commercial only. Not compatible.
- **Apache 2.0, BSD, ISC, MPL 2.0**: generally fine with MIT.

## Commercial Use

The tool is free. Anyone can build a paid product on top of it. Contributors should not add dependencies that prohibit commercial use without explicit discussion and an ADR.
