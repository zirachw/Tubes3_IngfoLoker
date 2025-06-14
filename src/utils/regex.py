# src/utils/regex.py

import re
import json
from typing import Dict, List, Any

class Summary:
    """Utility class for extracting structured information from raw text resumes."""

    @staticmethod
    def generate(raw_texts: Dict[int, str]) -> Dict[int, Dict[str, Any]]:
        results: Dict[int, Dict[str, Any]] = {}
        for detail_id, text in raw_texts.items():
            # 1) Normalize common UTF-8 mojibake back to proper Unicode
            try:
                text = text.encode('latin1').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass

            # 2) Remove placeholder “City , State” segments _in-line_, not entire lines
            clean_lines: List[str] = []
            for line in text.splitlines():
                # a) filter out any "Company Name ... City , State"
                line = re.sub(
                    r'Company Name.*?City\s*,\s*State',
                    '',
                    line,
                    flags=re.IGNORECASE
                )
                # b) filter out any junk (without company name) ending in "City , State"
                line = re.sub(
                    r'[^A-Za-z\n]*City\s*,\s*State',
                    '',
                    line,
                    flags=re.IGNORECASE
                )
                clean_lines.append(line)
            text = "\n".join(clean_lines)

            results[detail_id] = {
                "Summary":    Summary._extract_summary(text),
                "Skills":     Summary._extract_skills(text),
                "Experience": Summary._extract_experience_list(text),
                "Education":  Summary._extract_education_list(text),
            }
        return results


    @staticmethod
    def _find_section_content(text: str, section_pattern: str) -> str:
        lines = text.split('\n')
        section_start = -1
        for i, line in enumerate(lines):
            if re.search(rf"^({section_pattern})$", line.strip(), re.IGNORECASE):
                section_start = i + 1
                break
        if section_start == -1:
            return ""
        section_end = len(lines)
        majors = [
            r"^(Summary|Overview)$",
            r"^(Skills|Technical Skills|Highlights)$",
            r"^(Experience|Work History)$",
            r"^Education$",
            r"^(Interests|Additional Information|Accomplishments|Certifications)$"
        ]
        for i in range(section_start, len(lines)):
            if any(re.match(p, lines[i].strip(), re.IGNORECASE) for p in majors):
                section_end = i
                break
        return '\n'.join(lines[section_start:section_end]).strip()

    @staticmethod
    def _extract_summary(text: str) -> Dict[str, str]:
        content = Summary._find_section_content(text, r"(Summary|Overview)")
        if not content:
            return {"details": "-"}
        clean = re.sub(r'\s+', ' ', content.strip())
        if len(clean.split()) > 20:
            return {"details": clean}
        for para in content.split('\n\n'):
            cp = re.sub(r'\s+', ' ', para.strip())
            if len(cp.split()) > 20 and para.count('\n') > 1:
                return {"details": cp}
        if clean and len(clean.split()) > 5:
            return {"details": clean}
        for line in content.split('\n'):
            cl = line.strip()
            if cl and len(cl.split()) > 3:
                return {"details": cl}
        return {"details": "-"}

    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        content = Summary._find_section_content(text, r"(Skills|Technical Skills|Highlights)")
        if not content:
            return ["-"]
        clean = re.sub(r'\s+', ' ', content.strip())
        skills: List[str] = []
        if ',' in clean:
            for s in clean.split(','):
                s = re.sub(r':.*$', '', s).strip()
                if s and len(s) > 1 and len(s.split()) <= 4:
                    skills.append(s)
        if len(skills) <= 3:
            skills = []
            for line in content.split('\n'):
                cl = line.strip()
                if not cl:
                    continue
                if ':' in cl:
                    parts = cl.split(':', 1)
                    if len(parts) == 2:
                        for sub in re.split(r'[/,]', parts[1].strip()):
                            sub = sub.strip()
                            if sub and len(sub) > 1:
                                skills.append(sub)
                else:
                    if len(cl.split()) <= 4:
                        skills.append(cl)
        if len(skills) <= 2:
            skills = []
            for w in re.findall(r'\b[A-Za-z][A-Za-z\s]{2,15}\b', clean)[:10]:
                w = w.strip()
                if w and w.lower() not in ['skills', 'technical', 'highlights']:
                    skills.append(w)
        return skills or ["-"]

    @staticmethod
    def _extract_experience_list(text: str) -> List[Dict[str, str]]:
        section = Summary._find_section_content(text, r"(Experience|Work History)")
        if not section:
            return [{"interval": "-", "role": "-", "details": "-"}]

        lines = section.split('\n')
        patterns = [
            r'(\d{1,2}/\d{4})\s+to\s+(\d{1,2}/\d{4}|Current)',
            r'(\w+ \d{4})\s+to\s+(\w+ \d{4}|Current)',
            r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)',
        ]
        idxs: List[int] = []
        for i, line in enumerate(lines):
            if any(re.search(p, line, re.IGNORECASE) for p in patterns):
                idxs.append(i)
        if not idxs:
            return [Summary._extract_experience_item(section)]

        entries: List[Dict[str, str]] = []
        for i, start in enumerate(idxs):
            end = idxs[i+1] if i+1 < len(idxs) else len(lines)
            block = '\n'.join(lines[start:end])
            entries.append(Summary._extract_experience_item(block))
        return entries

    @staticmethod
    def _extract_experience_item(text: str) -> Dict[str, str]:
        lines = text.split('\n')
        # interval
        interval = "-"
        for line in lines:
            for pat in [
                r'(\d{1,2}/\d{4})\s+to\s+(\d{1,2}/\d{4}|Current)',
                r'(\w+ \d{4})\s+to\s+(\w+ \d{4}|Current)',
                r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)',
            ]:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    interval = m.group(0)
                    break
            if interval != "-":
                break
        # role
        role = "-"
        for line in lines:
            cl = line.strip()
            if re.search(r'\d{4}', cl):
                if re.search(r'\b(Senior|Junior|Lead|Principal|Chief|Head|Vice President|VP|Manager|Director|Analyst|Accountant|Developer|Engineer|Specialist|Coordinator|Assistant|Associate)\b', cl, re.IGNORECASE):
                    m = re.search(
                        r'([A-Za-z\s]*(Senior|Junior|Lead|Principal|Chief|Head|Vice President|VP|Manager|Director|Analyst|Accountant|Developer|Engineer|Specialist|Coordinator|Assistant|Associate)[A-Za-z\s]*)',
                        cl, re.IGNORECASE
                    )
                    if m:
                        pot = re.sub(r'Company Name', '', m.group(1), flags=re.IGNORECASE).strip()
                        if len(pot.split()) < 6:
                            role = pot
                            break
            else:
                words = cl.split()
                if 2 <= len(words) <= 8 and re.search(
                    r'\b(Senior|Junior|Lead|Principal|Chief|Head|Vice President|VP|Manager|Director|Analyst|Accountant|Developer|Engineer|Specialist|Coordinator|Assistant|Associate)\b',
                    cl, re.IGNORECASE
                ):
                    role = cl
                    break
            if role != "-":
                break
        # details
        details = "-"
        for line in lines:
            cl = line.strip()
            if (
                len(cl.split()) > 8 and
                not re.search(r'\d{4}', cl) and
                'Company Name' not in cl and
                'City , State' not in cl
            ):
                s = re.search(r'^([^.]+\.)', cl)
                if s:
                    details = s.group(1).strip()
                elif len(cl) < 200:
                    details = cl
                break
        return {"interval": interval, "role": role, "details": details}

    @staticmethod
    def _extract_education_list(text: str) -> List[Dict[str, str]]:
        section = Summary._find_section_content(text, r"Education")
        if not section:
            return [{"year": "-", "degree": "-", "school": "-"}]

        # Split into non-empty lines
        lines = [l.strip() for l in section.split('\n') if l.strip()]

        # Identify indices of lines that start a new education entry
        idxs = [
            i for i, line in enumerate(lines)
            if re.search(r'\b(19\d{2}|20\d{2})\b', line)
            or re.search(r'\b(Bachelor|Master|PhD|Associate|Diploma)\b', line, re.IGNORECASE)
        ]

        # If no entry markers found, treat entire section as one block
        if not idxs:
            blocks = [' '.join(lines)]
        else:
            blocks = []
            for j, start in enumerate(idxs):
                end = idxs[j+1] if j+1 < len(idxs) else len(lines)
                blocks.append(' '.join(lines[start:end]))

        entries: List[Dict[str, str]] = []
        for block in blocks:
            # Year
            years = re.findall(r'\b(19\d{2}|20\d{2})\b', block)
            year = years[0] if years else "-"

            # Degree
            degree = "-"
            for pat in [
                r"(Master[^,\n.]*)",
                r"(Bachelor[^,\n.]*)",
                r"(PhD[^,\n.]*)",
                r"(Associate[^,\n.]*)",
                r"(Doctorate[^,\n.]*)",
                r"(MBA[^,\n.]*)",
                r"(MS[^,\n.]*)",
                r"(BS[^,\n.]*)",
                r"(BA[^,\n.]*)"
            ]:
                m = re.search(pat, block, re.IGNORECASE)
                if m:
                    degree = m.group(1).strip()
                    degree = re.sub(r'\s*:\s*', ' in ', degree)
                    degree = re.sub(r'\s+', ' ', degree)
                    break

            # School
            school = "-"
            for pat in [
                r'([A-Z][A-Za-z\s&]+(?:University|College|School|Institute)[^,\n.]*)',
                r'(University of [A-Za-z\s]+)',
                r'([A-Z][A-Za-z]+\s+University)',
                r'([A-Z][A-Za-z]+\s+College)'
            ]:
                m = re.search(pat, block)
                if m:
                    school = m.group(1).strip()
                    school = re.sub(r',.*$', '', school)
                    school = re.sub(r'\s+', ' ', school)
                    break

            # Fallback school extraction
            if school == "-":
                for line in block.split('\n'):
                    caps = re.findall(r'\b[A-Z][A-Za-z]+\b', line.strip())
                    filtered = [
                        w for w in caps
                        if w.lower() not in [
                            'bachelor','master','degree','gpa',
                            'city','state','accounting','business','administration'
                        ]
                    ]
                    if len(filtered) >= 2:
                        school = ' '.join(filtered[:3])
                        break

            entries.append({"year": year, "degree": degree, "school": school})

        return entries

    @staticmethod
    def export_to_json(
        data: Dict[int, Dict[str, Any]],
        filepath: str
    ) -> None:
        """
        Save the extracted data structure to a JSON file.
        :param data: output of Summary.generate()
        :param filepath: path to write the JSON to
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)