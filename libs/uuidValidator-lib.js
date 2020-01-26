export default uuid => {
  // uuid validation regex from:
  // https://stackoverflow.com/questions/7905929/how-to-test-valid-uuid-guid
  const regex = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

  if (Array.isArray(uuid)) {
    let isOK = true;
    uuid.forEach(value => {
      if (!regex.test(value)) isOK = false;
    });
    return isOK;
  } else if (typeof uuid === 'string') {
    return regex.test(uuid);
  } else {
    return false;
  }
};
