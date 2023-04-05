const firstFollow = require('./firstFollow');
const fs = require('fs')
const rules = require('./rules')

// Read rules.json file for the rules
ff_rules = []
for (let i in rules) {
    rule_set = rules[i]
    for (const name in rule_set) {
        rights = rule_set[name]
        for (let rule in rights) {
            ff_rules.push({left: name, right: rights[rule]})
        }
    }
}

// Build rules suited for firstFollow module
const { firstSets, followSets, predictSets } = firstFollow(ff_rules)

// Create output JSON
output = {}

counter = 1

for (let i in rules) {
    let rule_set = rules[i]
    for (const name in rule_set) {
        let rights = rule_set[name]
        let rule = {first: firstSets[name], follow: followSets[name]}
        let rules_combined = []
        for (let rule in rights) {
            rules_combined.push({rule: rights[rule], prediction: predictSets[counter]})
            counter += 1
        }
        rule['rules'] = rules_combined
        output[name] = rule
    }
}

// Save it to grammar.json
data = JSON.stringify(output)
fs.writeFile("grammar.json", data, (err) => {
    if (err)
      console.log(err);
  });