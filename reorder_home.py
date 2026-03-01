import re

with open('dashboard/src/pages/Home.jsx', 'r') as f:
    content = f.read()

# Split into parts
# part 1: up to SECTION B
# part 2: SECTION B
# part 3: SECTION C
# part 4: SECTION D onwards

matches = list(re.finditer(r'\{/\*\s*=========================================\s*SECTION [B-D]', content))

if len(matches) == 3:
    b_start = matches[0].start()
    c_start = matches[1].start()
    d_start = matches[2].start()
    
    part1 = content[:b_start]
    part2 = content[b_start:c_start]
    part3 = content[c_start:d_start]
    part4 = content[d_start:]
    
    # Rename Section headers
    part3_renamed = part3.replace('SECTION C: THE DILEMMA & GOALS', 'SECTION B: THE MANIFESTO')
    part2_renamed = part2.replace('SECTION B: FEATURES', 'SECTION C: FEATURES')
    
    # Apply copy changes to the manifesto
    part3_renamed = part3_renamed.replace("The Vibe-Coder's Dilemma", "Our Manifesto")
    part3_renamed = part3_renamed.replace("AI writes the code.<br />\n                                <span className=\"text-neutral-500\">Who checks the locks?</span>", "Security shouldn't be<br />\n                                <span className=\"text-neutral-500\">an enterprise luxury.</span>")
    part3_renamed = part3_renamed.replace('Generative AI has killed the execution barrier, but the stigma remains: <span className="text-rose-400">"AI code is insecure."</span>\n                                <br /><br />\n                                Traditional security tools are built for enterprise DevOps teams. They cost thousands, require complex CI/CD tuning, and vomit false-positives that paralyze solo founders.', 'Traditional security tools are built for massive DevOps teams. They cost thousands, require complex CI/CD tuning, and vomit false-positives that paralyze indie makers.\n                                <br /><br />\n                                Generative AI has killed the execution barrier, but the stigma remains: <span className="text-rose-400">"AI code is insecure."</span> We are here to change that.')
    part3_renamed = part3_renamed.replace("01 // The Goal", "01 // The Solution")
    part3_renamed = part3_renamed.replace("Absolute Security", "Security for Everyone")
    
    new_content = part1 + part3_renamed + part2_renamed + part4
    
    with open('dashboard/src/pages/Home.jsx', 'w') as f:
        f.write(new_content)
    print("Successfully reordered Home.jsx")
else:
    print("Regex failed to find sections")
