DISCORD_TOKEN: str
with open("/run/secrets/discord_token", encoding="UTF-8") as secret:
    DISCORD_TOKEN = secret.readline().rstrip("\n")

DRIVE_LINKS = {
    "1e Bachelor": "https://drive.google.com/drive/folders/1wVpaBTF-s7UOCdFaIBIplzYsusskMBcn?usp=sharing",
    "2e Bachelor": "https://drive.google.com/drive/folders/1cpEQnaghjK1zy56QDIi-P16No-mKnnav?usp=sharing",
    "Nuttige Info": "https://drive.google.com/drive/folders/1L6ne7AACpmJSmz8fzYGWe5t8sK8j06NI?usp=sharing",
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
    "*snorts a line of coke*",
]
