const RandomGenerator = (() => {
    const SURNAMES = ['李','王','张','刘','陈','杨','赵','黄','周','吴'];
    const GIVEN_NAMES = {
        male: ['辰','轩','宇','泽','豪','杰','霖','浩','博','涛'],
        female: ['雨','琪','梦','雪','霜','露','月','云','诗','画']
    };

    function randInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function generateRandomCharacter() {
        const isMale = Math.random() > 0.5;
        const surname = SURNAMES[randInt(0, SURNAMES.length - 1)];
        const givenName = isMale ?
            GIVEN_NAMES.male[randInt(0, GIVEN_NAMES.male.length - 1)] :
            GIVEN_NAMES.female[randInt(0, GIVEN_NAMES.female.length - 1)];

        const attrs = {
            root: randInt(1, 10),
            comprehension: randInt(1, 10),
            physique: randInt(1, 10),
            spirit: randInt(1, 10),
            insight: randInt(1, 10),
            will: randInt(1, 10),
            charisma: randInt(1, 10),
            fortune_val: randInt(1, 10)
        };

        const fortuneTier = typeof getTier === 'function' ? getTier(attrs.fortune_val).name.toLowerCase() : 'ren';
        const fortuneList = typeof FORTUNES !== 'undefined' && FORTUNES[fortuneTier] ? FORTUNES[fortuneTier] : [];
        const destiny = typeof DESTINIES !== 'undefined' && DESTINIES.length ? DESTINIES[randInt(0, DESTINIES.length - 1)] : '';
        const fortune = fortuneList.length ? fortuneList[randInt(0, fortuneList.length - 1)] : '';

        return {
            name: surname + givenName,
            age: randInt(14, 30),
            attrs,
            destiny: [destiny],
            fortune,
            fortune_tier: fortuneTier
        };
    }

    return { randInt, generateRandomCharacter };
})();

window.randomGenerator = RandomGenerator;
