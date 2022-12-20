import os

import discord

DISCORD_TOKEN: str
with open("/run/secrets/discord_token") as secret:
    DISCORD_TOKEN = secret.readline().rstrip("\n")

GMAIL_APP_PASSWORD: str
with open("/run/secrets/gmail_app_password") as secret:
    GMAIL_APP_PASSWORD = secret.readline().rstrip("\n")

GUILD_ID = discord.Object(id=int(os.environ.get("GUILD_ID")))

VERIFIED_ROLE = os.environ.get("VERIFIED_ROLE")

VERIFY_CHANNEL = os.environ.get("VERIFY_CHANNEL")

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
_NL = "\n"
CALENDAR_TEMPLATE = f"""
<svg
    xlmns="http://www.w3.org/2000/svg"
    width="{_SVG_WIDTH}"
    height="{_SVG_HEIGHT}"
    viewBox="0 0 {_SVG_WIDTH} {_SVG_HEIGHT}"
    fill="#202020"
    stroke="none"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    font="20px sans-serif"
>
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

    <!-- Weekday planners -->
    <g>
        {_NL.join(
            f'''
            <g>
                <rect x="{_DAY_WIDTH * i + _HOUR_WIDTH}" y="{_HEADER_HEIGHT}" width="{_DAY_WIDTH}" height="{_SVG_HEIGHT}"/>
                {f"{{planner{i}}}"}
            </g>
            '''
            for i in range(7)
        )}
    </g>

    <!-- Lines are drawn last so they don't get covered up -->

    <!-- Hour division lines -->
    <g stroke="#928374">
        {_NL.join(
            f'<line x1="0" y1="{_HOUR_HEIGHT * i + _HEADER_HEIGHT}" x2="{_SVG_WIDTH}" y2="{_HOUR_HEIGHT * i + _HEADER_HEIGHT}"/>'
            for i in range(1,10)
        )}
    </g>

    <!-- Weekday division lines -->
    <g stroke="#928374">
        {_NL.join(
            f'<line x1="{_DAY_WIDTH * i + _HOUR_WIDTH}" y1="0" x2="{_DAY_WIDTH * i + _HOUR_WIDTH}" y2="{_SVG_HEIGHT}"/>'
            for i in range(1,7)
        )}
    </g>

    <!-- Outer box -->
    <g stroke-width="4" stroke="#ec9635">
        <line x1="0" y1="0" x2="{_SVG_WIDTH}" y2="0"/>
        <line x1="{_SVG_WIDTH}" y1="0" x2="{_SVG_WIDTH}" y2="{_SVG_HEIGHT}"/>
        <line x1="{_SVG_WIDTH}" y1="{_SVG_HEIGHT}" x2="0" y2="{_SVG_HEIGHT}"/>
        <line x1="0" y1="{_SVG_HEIGHT}" x2="0" y2="0"/>
    </g>

    <!-- Hour division line -->
    <line stroke="#ec9635" x1="{_HOUR_WIDTH}" y1="0" x2="{_HOUR_WIDTH}" y2="{_SVG_HEIGHT}"/>

    <!-- Header division line -->
    <line stroke="#ec9635" x1="0" y1="{_HEADER_HEIGHT}" x2="{_SVG_WIDTH}" y2="{_HEADER_HEIGHT}"/>
</svg>
"""


def day_to_planner(day_info: list[dict[str, str]]) -> str:
    """
    Convert a list of classes happening on a given day to a visual
    representation using svg elements
    """

    return ""
