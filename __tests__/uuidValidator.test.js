import uuidValidator from '../libs/uuidValidator-lib';

test('Single valid uuid', () => {
  const isUUID = uuidValidator('db758d4b-8721-4866-b07c-06faece1991c');
  expect(isUUID).toEqual(true);
});

test('Single unvalid uuid', () => {
  const isUUID = uuidValidator('db758d4b-8721-4866-b07c-06faece19');
  expect(isUUID).toEqual(false);
});

test(`Array of valid uuids`, () => {
  const isUUID = uuidValidator([
    '01A16D95-274F-48A0-8B51-245AC80082AB',
    'db758d4b-8721-4866-b07c-06faece1991c',
    '0DE820CC-F55D-4D29-8CA8-C3B48DDDE890'
  ]);
  expect(isUUID).toEqual(true);
});

test(`Array of invalid uuids`, () => {
  const isUUID = uuidValidator([
    '01A16D95-274F-48A0-8B51-245AC80',
    'db758d4b-8721-4866-b07c-06faece',
    '0DE820CC-F55D-4D29-8CA8-C3B48DD'
  ]);
  expect(isUUID).toEqual(false);
});

test(`Array of valid uuids containing one invalid uuid`, () => {
  const isUUID = uuidValidator([
    '01A16D95-274F-48A0-8B51-245AC80082AB',
    'db758d4b-8721-4866-b07c-06faece1991c',
    '01A16D95-274F-48A0-8B51-245AC80',
    '0DE820CC-F55D-4D29-8CA8-C3B48DDDE890'
  ]);
  expect(isUUID).toEqual(false);
});
