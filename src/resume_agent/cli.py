import argparse
import sys

from resume_agent.loaders import load_jd_text, InputError, load_resume
from resume_agent.jd_extractor import extract_jd

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog = "resume-agent",
        description="Match a resume against a job description (local LangChain agent).",
    )

    parser.add_argument("--jd", required=True, help="Path to job description (.txt)")
    parser.add_argument("--resume", required=True, help="Path to resume  (.txt)")
    parser.add_argument("--out", required=False, help="Optional path to save JSON result")
    parser.add_argument("--debug", action="store_true", help="Print Extra debug info (used more in later sections)")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    
    try:
        jd_text = load_jd_text(args.jd)
        resume_text = load_resume(args.resume)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    

    print(f"JD loaded: {len(jd_text)} character from {args.jd}")
    print(f"Resume loaded: {len(resume_text)} character from {args.resume}")
    if args.out:
        print(f"Output path (not used yet): {args.out}")
    if args.debug:
        print("--- Extracted Job Requirements ---")
        requirement = extract_jd(jd_text)
        print(requirement.model_dump_json(indent=2))
        # print(jd_text[:200])
        # print("--- Resume preview ---")
        # print(resume_text[:200])    

