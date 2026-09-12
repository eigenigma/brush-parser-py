use brush_parser::{ParserImpl, ParserOptions};

/// Always selects the PEG implementation; the entry points expose no choice of
/// `parser_impl`.
pub fn parser_options(
    enable_extended_globbing: bool,
    posix_mode: bool,
    sh_mode: bool,
    tilde_expansion_at_word_start: bool,
    tilde_expansion_after_colon: bool,
) -> ParserOptions {
    ParserOptions {
        enable_extended_globbing,
        posix_mode,
        sh_mode,
        tilde_expansion_at_word_start,
        tilde_expansion_after_colon,
        parser_impl: ParserImpl::Peg,
    }
}
