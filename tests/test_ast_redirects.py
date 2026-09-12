import pytest

from brush_parser import _core as core
from tests._helpers import first_command, narrow, span, suffix_items, word


def redirect(text: str) -> core.IoRedirect:
    items = suffix_items(text)
    assert len(items) == 1
    return narrow(items[0], core.CommandPrefixOrSuffixItem.IoRedirect).redirect


def file_redirect(text: str) -> core.IoRedirect.File:
    return narrow(redirect(text), core.IoRedirect.File)


def here_document(text: str) -> core.IoRedirect.HereDocument:
    return narrow(redirect(text), core.IoRedirect.HereDocument)


@pytest.mark.parametrize(
    ("operator", "kind"),
    [
        ("<", core.IoFileRedirectKind.Read),
        (">", core.IoFileRedirectKind.Write),
        (">>", core.IoFileRedirectKind.Append),
        ("<>", core.IoFileRedirectKind.ReadAndWrite),
        (">|", core.IoFileRedirectKind.Clobber),
    ],
)
def test_file_redirect_kinds(operator, kind):
    text = f"cat {operator} f"
    assert redirect(text) == core.IoRedirect.File(
        None, kind, core.IoFileRedirectTarget.Filename(word("f", len(text) - 1))
    )


@pytest.mark.parametrize(
    ("text", "fd", "kind", "target"),
    [
        ("cat <&3", None, core.IoFileRedirectKind.DuplicateInput, "3"),
        ("cat 3<&0", 3, core.IoFileRedirectKind.DuplicateInput, "0"),
        ("cat 2>&1", 2, core.IoFileRedirectKind.DuplicateOutput, "1"),
        ("cat 3>&-", 3, core.IoFileRedirectKind.DuplicateOutput, "-"),
    ],
)
def test_duplicate_redirects(text, fd, kind, target):
    parsed = file_redirect(text)
    assert parsed.fd == fd
    assert parsed.kind == kind
    assert parsed.target == core.IoFileRedirectTarget.Duplicate(
        word(target, len(text) - 1)
    )


def test_process_substitution_target():
    parsed = file_redirect("cat < <(x)")
    assert parsed.kind == core.IoFileRedirectKind.Read
    target = narrow(parsed.target, core.IoFileRedirectTarget.ProcessSubstitution)
    assert target.kind == core.ProcessSubstitutionKind.Read
    assert target.command.loc == span(7, 10)


def test_fd_target_is_constructible():
    target = core.IoFileRedirectTarget.Fd(4)
    assert target.fd == 4
    assert target == core.IoFileRedirectTarget.Fd(4)


def test_here_document_with_tab_removal_and_expansion():
    parsed = here_document("cat <<-EOF\n\tx\nEOF\n")
    assert parsed.fd is None
    assert parsed.document.remove_tabs is True
    assert parsed.document.requires_expansion is True
    assert parsed.document.here_end == word("EOF", 7)
    assert parsed.document.doc.value == "x\n"


def test_quoted_here_document_delimiter_disables_expansion():
    parsed = here_document("cat <<'EOF'\n$x\nEOF\n")
    assert parsed.document.remove_tabs is False
    assert parsed.document.requires_expansion is False
    assert parsed.document.here_end.value == "'EOF'"
    assert parsed.document.doc.value == "$x\n"


def test_here_document_body_span_is_upstream_char_indexed():
    parsed = here_document("cat <<EOF\nx\nEOF\n")
    assert parsed.document.doc.loc == core.SourceSpan(
        core.SourcePosition(10, 2, 1), core.SourcePosition(16, 4, 1)
    )


def test_here_string():
    assert redirect("cat <<< w") == core.IoRedirect.HereString(None, word("w", 8))
    assert narrow(redirect("cat 3<<< w"), core.IoRedirect.HereString).fd == 3


def test_output_and_error():
    assert redirect("cat &>f") == core.IoRedirect.OutputAndError(
        word("f", 6), append=False
    )
    assert redirect("cat &>>f") == core.IoRedirect.OutputAndError(
        word("f", 7), append=True
    )


def test_redirect_list_order():
    command = narrow(first_command("{ a; } >f 2>&1"), core.Command.Compound)
    assert command.redirects is not None
    assert [type(item).__qualname__ for item in command.redirects.items] == [
        "IoRedirect.File",
        "IoRedirect.File",
    ]
    assert narrow(command.redirects.items[1], core.IoRedirect.File).fd == 2
