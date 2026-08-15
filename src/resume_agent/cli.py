import argparse
import sys

from resume_agent.loaders import load_jd_text, InputError

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog = "resume-agent",
        description="Match a resume against a job description (local LangChain agent).",
    )

    parser.add_argument("--jd", required=True, help="Path to job description (.txt)")
    parser.add_argument("--resume", required=False, help="Path to resume  (.txt)")
    parser.add_argument("--out", required=False, help="Optional path to save JSON result")
    parser.add_argument("--debug", action="store_true", help="Print Extra debug info (used more in later sections)")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    
    try:
        jd_text = load_jd_text(args.jd)
     
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    

    print(f"JD loaded: {len(jd_text)} character from {args.jd}")
    
    if args.out:
        print(f"Output path (not used yet): {args.out}")
    if args.debug:
        print("--- JD preview ---")
        print(jd_text[:200])
        print("--- Resume preview ---")
        print(resume_text[:200])    

