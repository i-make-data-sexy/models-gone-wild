/* ========================================================================
     About This File
   ======================================================================== */

/* The glossary, each security term with its definition, which the page
   script reads as GLOSSARY to mark the terms in every case's prose. The
   add-case skill adds a term here whenever a new case needs one. Loads
   before the page script. */



/* ========================================================================
     Glossary
   ======================================================================== */

const GLOSSARY = {
    "ExploitGym evaluation":        "A run against ExploitGym, a public benchmark that tests whether an AI agent can turn a known bug into a working exploit. It covers 869 real vulnerabilities and was built by researchers at UC Berkeley, the Max Planck Institute, UC Santa Barbara, Arizona State, Anthropic, OpenAI, and Google.",
    "benchmark answer key":         "The worked solutions to the benchmark's tasks, which Hugging Face hosted alongside its models and datasets. A model holding them can score well without solving anything.",
    "three separate organizations": "Anthropic has not named them, to protect the companies affected. One had credentials and database contents read after a fictional target shared a domain with a real company. One was reached through a malicious package published to the real PyPI registry. The third was found after the model scanned roughly 9,000 targets.",
    "capture-the-flag":             "A security exercise scored on breaking into a deliberately vulnerable system and retrieving a planted token, the flag. It is how security teams train and how model cyber skills get benchmarked.",
    "zero-day":                     "A software flaw the vendor does not yet know about, so there is no patch available when someone first exploits it.",
    "sandbox":                      "An isolated environment a model is meant to run inside, walled off from real systems and the open internet.",
    "privilege escalation":         "Gaining a higher level of access than an account was granted, such as moving from an ordinary user to an administrator.",
    "lateral movement":             "Moving from the first machine reached onto other machines on the same network.",
    "SQL injection":                "Slipping database commands into an ordinary input field so the database runs them.",
    "open-weight":                  "A model whose weights anyone can download and run on their own hardware, rather than reaching it through a company's service.",
    "Hugging Face":                 "A widely used platform for hosting models, datasets, and evaluation benchmarks.",
    "Modal Labs":                   "A New York company that rents cloud computing for running AI code, including isolated sandboxes its customers can expose online.",
    "UK AI Security Institute":     "The UK government body that runs safety and security evaluations on frontier AI models.",
    "Irregular":                    "The third-party evaluation firm that ran the test.",
    "POST requests":                "Web requests that send data to a server, as opposed to GET requests, which only read from it. A proxy that allows GET but blocks POST lets a program browse the internet without being able to change anything on it.",
    "RubyGems":                     "The public package registry for the Ruby programming language, where developers publish and install code libraries called gems.",
    "RubyDoc.info":                 "A free service that builds and hosts documentation for published Ruby gems, running each gem's documentation settings on its own servers.",
    "remote code execution":        "Running your own commands on somebody else's machine over a network.",
    "Victorian Agency for Health Information": "Victoria's health data agency, a division of the state Department of Health. It collects and reports data on the quality, safety, and performance of the state's health system and on the health of Victorians.",
    "Services Australia":           "The Australian government agency that runs Medicare, the country's public health insurance scheme, along with welfare and child support payments.",
    "urlquery.net":                 "A public service that loads a web address in its own browser to check it for threats, then publishes the result. The agents drove it as a browser from outside their own network limits.",
    "XSS":                          "Cross-site scripting. Getting a site to accept script that then runs in other visitors' browsers. A probe tests whether the site will take it.",
    "pre-production server":        "A copy of a website used to test changes before they go live. It may not sit behind the same protections as the public site.",
    "Data USA":                     "An open-access site for United States government data, run jointly by Deloitte, Datawheel, and MIT's Collective Learning Group.",
    "Office for Civil Rights":      "The Education Department office that enforces federal civil rights laws in schools and colleges that receive federal money, and investigates discrimination complaints.",
    "Investor.gov":                 "The SEC's website for individual investors, with guides, alerts, and tools for checking a financial professional's background.",
    "Transluce":                    "A nonprofit research lab that builds tools for understanding AI systems. It has been tracing AI agent activity on the open web, including attempted hacks it attributes to OpenAI agents.",
    "Etherpad":                     "A web editor where several people type into the same document at once. Wikimedia hosts a public copy for meeting notes and drafts.",
    "Wikidata Query Service":       "Wikimedia's public service for running database-style queries against Wikidata, the structured-data project that supplies facts to Wikipedia and other sites.",
    "proxy":                        "A server that fetches web pages on someone else's behalf, so the request appears to come from the proxy rather than from whoever asked for it.",
    "IP address":                   "The number that identifies a machine on a network, so other machines can find it and send it traffic.",
    "Tor":                          "A network that routes traffic through several volunteer relays so the origin of a request is hidden. Used here as a way to keep reaching the wiki from addresses not tied to the sandbox."
};