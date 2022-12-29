import datetime
import textwrap
import math


DISCORD_TOKEN: str
with open("/run/secrets/discord_token") as secret:
    DISCORD_TOKEN = secret.readline().rstrip("\n")

SMTP_USER: str
SMTP_PASSWORD: str
with open("/run/secrets/smtp_credentials") as secret:
    SMTP_USER = secret.readline().rstrip("\n")
    SMTP_PASSWORD = secret.readline().rstrip("\n")

DRIVE_LINKS = {
    "Grondslagen van de Psychologie": "https://drive.google.com/drive/folders/10ZKbgdHg49_DRjH5TtPtZ7sZjQt6GmMD?usp=sharing",
    "Kwalitatieve Data Analyse": "https://drive.google.com/drive/folders/10EKAngz_VfQzSQ1RKgZbvKOZ61SmEmMZ?usp=sharing",
    "Ontwikkelingspsychologie": "https://drive.google.com/drive/folders/1-AF5LQKTqdSFFAXBM49yk3o9UhnTLOFN?usp=sharing",
    "Sociale Psychologie": "https://drive.google.com/drive/folders/1-0tAWRMPh9m2RmZKrI6uNDVkSSmmFekh?usp=sharing",
    "Statistiek 1": "https://drive.google.com/drive/folders/1-6cUn4w0ixenP2UesO1qk3BK5-3f1-nl?usp=sharing",
    "Algemene Psychologie": "https://drive.google.com/drive/folders/1OXNVWr46Ihyne1pQ_QB5-0f_WJYy91G4?usp=sharing",
    "Differentiële Psychologie": "https://drive.google.com/drive/folders/1OXEmLY3tIlZdL9wNyerdrpFCWg4xZfKO?usp=sharing",
    "Erfelijkheidsleer": "https://drive.google.com/drive/folders/1OZnTXhyvYF87f7EK5_qN5BqZ5jNtvmTg?usp=sharing",
    "Introductie Cognitieve Psychologie 1": "https://drive.google.com/drive/folders/1O_oBm21jgn9_0c9OuZjc6PS1-AIq0AEw?usp=sharing",
    "Methodologie": "https://drive.google.com/drive/folders/1OuNgRibMgktYOPwTd2UiuREfRrctGURL?usp=sharing",
    "Maatschappelijke Structuren": "https://drive.google.com/drive/folders/1OpxdJA__BYx0RlsJIV8ei2zdWuZ_Mh45?usp=sharing",
}

FREUD_QUOTES = [
    "One day, in retrospect, the years of struggle will strike you as the most beautiful.",
    "Being entirely honest with oneself is a good exercise.",
    "Most people do not really want freedom, because freedom involves responsibility, and most people are frightened of responsibility.",
    "Unexpressed emotions will never die. They are buried alive and will come forth later in uglier ways.",
    "We are never so defenseless against suffering as when we love.",
    "Out of your vulnerabilities will come your strength.",
    "Where does a thought go when it's forgotten?",
    "He that has eyes to see and ears to hear may convince himself that no mortal can keep a secret. If his lips are silent, he chatters with his fingertips; betrayal oozes out of him at every pore.",
    "Religious doctrines are all illusions, they do not admit of proof, and no one can be compelled to consider them as true or to believe in them.",
    "A woman should soften but not weaken a man.",
    "It is impossible to escape the impression that people commonly use false standards of measurement that they seek power, success and wealth for themselves and admire them in others, and that they underestimate what is of true value in life.",
    "Everywhere I go I find a poet has been there before me.",
    "In the depths of my heart I can't help being convinced that my dear fellow-men, with a few exceptions, are worthless.",
    "In the depths of my heart I can't help being convinced that my dear fellow-men, with a few exceptions, are worthless.",
    "Immorality, no less than morality, has at all times found support in religion.",
    "The madman is a dreamer awake",
    "No, our science is no illusion. But an illusion it would be to suppose that what science cannot give us we can get elsewhere.",
    "The virtuous man contents himself with dreaming that which the wicked man does in actual life.",
    "He does not believe that does not live according to his belief.",
    "The behavior of a human being in sexual matters is often a prototype for the whole of his other modes of reaction in life.",
    "America is a mistake, a giant mistake.",
    "The intention that man should be happy is not in the plan of Creation.",
    "Men are more moral than they think and far more immoral than they can imagine.",
    "Love and work are the cornerstones of our humanness.",
    "The creative writer does the same as the child at play; he creates a world of fantasy which he takes very seriously.",
    "What progress we are making. In the Middle Ages they would have burned me. Now they are content with burning my books. ",
    "Loneliness and darkness have just robbed me of my valuables.",
    "Where id is, there shall ego be",
    "The ego is not master in its own house.",
    "How bold one gets when one is sure of being loved",
    "There are no mistakes",
    "I had thought about cocaine in a kind of day-dream.",
    "Smoking is indispensable if one has nothing to kiss",
    "Man has, as it were, become a kind of prosthetic God.",
    "Anatomy is destiny.",
    "When one does not have what one wants, one must want what one has.",
    "Places are often treated like persons.",
    "I do not in the least underestimate bisexuality. . . I expect it to provide all further enlightenment.",
    "In matters of sexuality we are at present, every one of us, ill or well, nothing but hypocrites.",
    "Dreams are never concerned with trivia.",
    "This is one race of people for whom psychoanalysis is of no use whatsoever. [speaking about the Irish]",
    "Woman ... what does she want?",
    "Sometimes a cigar is just a cigar.",
    "Therapeutic.",
    "If one of us should die, then I shall move to Paris.",
    "Where does a thought go when it's forgotten?",
    "I am going to the USA to catch sight of a wild porcupine and to give some lectures.",
    "Who lacks sex speaks about sex, hungry talks about food, a person who has no money - about money, and our oligarchs and bankers talk about morality",
    "Mathematics enjoys the greatest reputation as a diversion from sexuality. This had been the very advice to which Jean-Jacques Rousseau was obliged to listen from a lady who was dissatisfied with him: 'Lascia le donne e studia la matematica!' So too our fugitive threw himself with special eagerness into the mathematics and geometry which he was taught at school, till suddenly one day his powers of comprehension were paralysed in the face of some apparently innocent problems. It was possible to establish two of these problems; 'Two bodies come together, one with a speed of ... etc' and 'On a cylinder, the diameter of whose surface is m, describe a cone ... etc' Other people would certainly not have regarded these as very striking allusions to sexual events; but he felt that he had been betrayed by mathematics as well, and took flight from it too.",
]

TIMEEDIT_URL = "https://cloud.timeedit.net/ugent/web/guest/"

_SVG_WIDTH = 2800
_SVG_HEIGHT = 1200
_HEADER_HEIGHT = 120
_HOUR_WIDTH = 200

_DAY_WIDTH = (_SVG_WIDTH - _HOUR_WIDTH) / 7
_HOUR_HEIGHT = (_SVG_HEIGHT - _HEADER_HEIGHT) / 10

_TEXT_COLOR = "#f9f5d7"
_BG_COLOR = "#202020"
_LINE_GREY = "#928374"
_VPPK_ORANGE = "#ec9635"
_VPPK_ORANGE_DARK = "#2f1b04"
_NL = "\n"
CALENDAR_TEMPLATE = f"""<?xml version="1.0"?>
<svg
    xlmns="http://www.w3.org/2000/svg"
    version="1.2"
    baseProfile="tiny"
    width="{_SVG_WIDTH}"
    height="{_SVG_HEIGHT}"
    viewBox="0 0 {_SVG_WIDTH} {_SVG_HEIGHT}"
    fill="{_BG_COLOR}"
    stroke="none"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    font="20px sans-serif"
>
    <!-- Background -->
    <rect x="0" y="0" width="{_SVG_WIDTH}" height="{_SVG_HEIGHT}"/>

    <!-- Week indicator -->
    <g stroke="{_TEXT_COLOR}" stroke-width="1">
        <rect x="0" y="0" width="{_HOUR_WIDTH}" height="{_HEADER_HEIGHT}"/>
        <text x="{_HOUR_WIDTH / 2}" y="{_HEADER_HEIGHT / 2}" fill="{_TEXT_COLOR}" dominant-baseline="middle" text-anchor="middle">
            W {{week}}
        </text>
    </g>

    <!-- Hour indicators -->
    <g stroke="{_TEXT_COLOR}" stroke-width="1">
        {_NL.join(
            f'''
            <g>
                <rect x="0" y="{_HOUR_HEIGHT * i + _HEADER_HEIGHT}" width="{_HOUR_WIDTH}" height="{_HOUR_HEIGHT}"/>
                <text x="{_HOUR_WIDTH / 2}" y="{_HOUR_HEIGHT * (i+0.5) + _HEADER_HEIGHT}" fill="{_TEXT_COLOR}" dominant-baseline="middle" text-anchor="middle">
                    {f"{8+i:02d}:00"}
                </text>
            </g>
            '''
            for i in range(10)
        )}
    </g>

    <!-- Weekday dates -->
    <g stroke="{_TEXT_COLOR}" stroke-width="1">
        {_NL.join(
            f'''
            <g>
                <rect x="{_DAY_WIDTH * i + _HOUR_WIDTH}" y="0" width="{_DAY_WIDTH}" height="{_HEADER_HEIGHT}"/>
                <text x="{_DAY_WIDTH * (i+0.5) + _HOUR_WIDTH}" y="{_HEADER_HEIGHT / 2}" fill="{_TEXT_COLOR}" dominant-baseline="middle" text-anchor="middle">
                    {f"{{date{i}}}"}
                </text>
            </g>
            '''
            for i in range(7)
        )}
    </g>

    <!-- Hour division lines -->
    <g stroke="{_LINE_GREY}">
        {_NL.join(
            f'<line x1="0" y1="{_HOUR_HEIGHT * i + _HEADER_HEIGHT}" x2="{_SVG_WIDTH}" y2="{_HOUR_HEIGHT * i + _HEADER_HEIGHT}"/>'
            for i in range(1,10)
        )}
    </g>

    <!-- Weekday planners -->
    <g>
        {_NL.join(
            f'''
            <g>
                <rect x="{_DAY_WIDTH * i + _HOUR_WIDTH}" y="{_HEADER_HEIGHT}" width="{_DAY_WIDTH}" height="{_SVG_HEIGHT}" fill="none"/>
                {f"{{planner{i}}}"}
            </g>
            '''
            for i in range(7)
        )}
    </g>

    <!-- Lines are drawn last so they don't get covered up -->

    <!-- Weekday division lines -->
    <g stroke="{_LINE_GREY}">
        {_NL.join(
            f'<line x1="{_DAY_WIDTH * i + _HOUR_WIDTH}" y1="0" x2="{_DAY_WIDTH * i + _HOUR_WIDTH}" y2="{_SVG_HEIGHT}"/>'
            for i in range(1,7)
        )}
    </g>

    <!-- Outer box -->
    <g stroke-width="4" stroke="{_VPPK_ORANGE}">
        <line x1="0" y1="0" x2="{_SVG_WIDTH}" y2="0"/>
        <line x1="{_SVG_WIDTH}" y1="0" x2="{_SVG_WIDTH}" y2="{_SVG_HEIGHT}"/>
        <line x1="{_SVG_WIDTH}" y1="{_SVG_HEIGHT}" x2="0" y2="{_SVG_HEIGHT}"/>
        <line x1="0" y1="{_SVG_HEIGHT}" x2="0" y2="0"/>
    </g>

    <!-- Hour division line -->
    <line stroke="{_VPPK_ORANGE}" x1="{_HOUR_WIDTH}" y1="0" x2="{_HOUR_WIDTH}" y2="{_SVG_HEIGHT}"/>

    <!-- Header division line -->
    <line stroke="{_VPPK_ORANGE}" x1="0" y1="{_HEADER_HEIGHT}" x2="{_SVG_WIDTH}" y2="{_HEADER_HEIGHT}"/>
</svg>
"""


def day_to_planner(day_idx: int, day_infos: list[dict[str, str]]) -> str:
    """
    Convert a list of courses happening on a given day to a visual
    representation using svg elements
    """

    to_time = lambda d: datetime.datetime.strptime(d, "%d-%m-%YT%H:%M").timestamp()

    day_infos.sort(key=lambda i: to_time(f'{i["start_date"]}T{i["start_time"]}'))

    # Group the day_infos into non-overlapping groups
    # If two day_infos overlap, they'll be in the same group
    day_info_groups: list[list[dict[str, str]]] = []
    day_info_group_idx = 0
    for day_info in day_infos:
        if day_info_group_idx == len(day_info_groups):
            day_info_groups.append([day_info])
            continue

        is_new_group = True

        for grouped_day_info in day_info_groups[day_info_group_idx]:
            if to_time(
                f'{grouped_day_info["start_date"]}T{grouped_day_info["end_time"]}'
            ) > to_time(f'{day_info["start_date"]}T{day_info["start_time"]}'):
                day_info_groups[day_info_group_idx].append(day_info)
                is_new_group = False
                break

        if is_new_group:
            day_info_group_idx += 1
            day_info_groups.append([day_info])

    return "\n".join(_group_to_items(day_idx, group) for group in day_info_groups)


def _group_to_items(day_idx: int, group: list[dict[str, str]]) -> str:
    width = _DAY_WIDTH / len(group)

    items = []
    for [info_idx, day_info] in enumerate(group):
        x = _HOUR_WIDTH + _DAY_WIDTH * day_idx + width * info_idx
        y_start = _time_to_y_coord(day_info["start_time"])
        y_end = _time_to_y_coord(day_info["end_time"])
        height = y_end - y_start

        items.append(
            f"""
            <g>
                <rect
                    x="{x}"
                    y="{y_start}"
                    width="{width}"
                    height="{height}"
                    fill="{_VPPK_ORANGE_DARK}"
                    stroke="{_VPPK_ORANGE}"
                />
                <text
                    x="{x + width/2}"
                    y="{y_start}"
                    fill="{_TEXT_COLOR}"
                    stroke="{_TEXT_COLOR}"
                    font="20px monospace"
                    dominant-baseline="middle"
                    text-anchor="middle"
                >
                    {_make_wrapped_text(x, y_start, width, height, day_info)}
                </text>
            </g>
        """
        )

    return "\n".join(items)


def _time_to_y_coord(time: str) -> int:
    hours = int(time.split(":")[0])
    minutes = int(time.split(":")[1])

    return (
        _HEADER_HEIGHT + ((hours - 8) * _HOUR_HEIGHT) + ((minutes / 60) * _HOUR_HEIGHT)
    )


def _make_wrapped_text(
    x: int, y: int, width: int, height: int, info: dict[str, str]
) -> str:
    name_text = info["course_name"]
    time_text = f"{info['start_time']} - {info['end_time']}"
    loc_text = f'{info["classroom"]}, {info["building"]}, {info["campus"]}'

    chars_per_line = math.floor(width / (20 / 1.5))
    max_lines = math.floor(height / (20 * 1.2))

    name_lines = textwrap.wrap(name_text, chars_per_line)
    time_lines = textwrap.wrap(time_text, chars_per_line)
    loc_lines = textwrap.wrap(loc_text, chars_per_line)

    lines = name_lines + time_lines + loc_lines
    stripped_lines = lines[:max_lines]

    if len(lines) != len(stripped_lines):
        stripped_lines[-1] = stripped_lines[-1][:-4] + "..."

    return f"""
        <g>
            {_NL.join(
                f'<tspan x="{x + width/2}" dy="1.2em">{line}</tspan>'
                for line in stripped_lines
            )}
        </g>
    """
