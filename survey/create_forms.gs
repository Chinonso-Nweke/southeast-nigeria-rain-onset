// Creates two Google Forms: an anonymous rain survey, and a separate volunteer form.
// Run createForms() once. The links appear in View > Logs (or the Execution log).

function createForms() {
  var survey = FormApp.create('Rain and planting in south-east Nigeria: farmer survey');
  survey.setCollectEmail(false);
  survey.setLimitOneResponsePerUser(false);
  survey.setDescription(
    'This is a university research project on rainfall and planting in south-east Nigeria. ' +
    'It is voluntary and anonymous. You do not need to give your name. It takes about 5 minutes. ' +
    'You can answer in English, Pidgin or Igbo.\n\n' +
    'Dis na university research about rain and farming for south-east Nigeria. Na your choice to answer. ' +
    'You no need give your name. E go take like 5 minutes. (Pidgin draft: please check it.)');
  survey.setConfirmationMessage('Thank you. Your answers will help us understand how the rains are changing.');

  var consent = survey.addMultipleChoiceItem().setTitle('Do you agree to take part?').setRequired(true);
  consent.setChoices([
    consent.createChoice('Yes, I agree', FormApp.PageNavigationType.CONTINUE),
    consent.createChoice('No', FormApp.PageNavigationType.SUBMIT)
  ]);

  survey.addPageBreakItem().setTitle('About your farming');
  survey.addMultipleChoiceItem().setTitle('Which place do you farm nearest to?')
    .setChoiceValues(['Enugu', 'Nsukka', 'Abakaliki', 'Onitsha', 'Owerri']).showOtherOption(true).setRequired(true);
  survey.addMultipleChoiceItem().setTitle('How many years have you farmed here?')
    .setChoiceValues(['Under 5', '5 to 10', '11 to 20', '21 to 30', 'Over 30']).setRequired(true);
  survey.addCheckboxItem().setTitle('What are your main crops?')
    .setChoiceValues(['Cassava', 'Yam', 'Maize', 'Rice', 'Vegetables']).showOtherOption(true);
  survey.addMultipleChoiceItem().setTitle('In a normal year, when do you plant your main crop after the first real rains?')
    .setChoiceValues(['February or earlier', 'March', 'April', 'May', 'June or later']);

  survey.addPageBreakItem().setTitle('How the rains have changed');
  var change = ['Much earlier', 'A little earlier', 'The same', 'A little later', 'Much later', 'Not sure'];
  survey.addMultipleChoiceItem().setTitle('Compared with 20 to 30 years ago, the rains now start:')
    .setChoiceValues(change).setRequired(true);
  survey.addMultipleChoiceItem().setTitle('Compared with 20 to 30 years ago, the total rain in a year is:')
    .setChoiceValues(['Much less', 'Less', 'The same', 'More', 'Much more', 'Not sure']).setRequired(true);

  var years = [];
  for (var y = 2005; y <= 2025; y++) years.push(String(y));
  survey.addPageBreakItem().setTitle('Years you remember').setHelpText('Only tick the years you remember clearly. It is fine to leave these blank.');
  survey.addCheckboxItem().setTitle('Which years do you clearly remember as a LATE start of the rains?').setChoiceValues(years);
  survey.addCheckboxItem().setTitle('Which years do you remember as an EARLY start of the rains?').setChoiceValues(years);
  survey.addCheckboxItem().setTitle('In which years did you lose seedlings to a dry spell after planting?').setChoiceValues(years);

  survey.addPageBreakItem().setTitle('In your own words');
  survey.addParagraphTextItem().setTitle('How have the rains changed over the years? (any language)');

  var vol = FormApp.create('Daily rain reports: volunteer sign-up');
  vol.setCollectEmail(false);
  vol.setDescription(
    'Optional. If you are willing to send a very short rain report on WhatsApp or SMS from March, leave a way to reach you. ' +
    'Your contact details are kept private and are never published or linked to the survey.');
  vol.setConfirmationMessage('Thank you. We will contact you before the rainy season starts.');
  vol.addMultipleChoiceItem().setTitle('Which place do you farm nearest to?')
    .setChoiceValues(['Enugu', 'Nsukka', 'Abakaliki', 'Onitsha', 'Owerri']).showOtherOption(true).setRequired(true);
  vol.addTextItem().setTitle('WhatsApp number or email').setRequired(true);
  vol.addMultipleChoiceItem().setTitle('Preferred way to send reports')
    .setChoiceValues(['WhatsApp', 'SMS', 'Either']);

  Logger.log('SURVEY (share this link): ' + survey.getPublishedUrl());
  Logger.log('SURVEY (edit link, keep private): ' + survey.getEditUrl());
  Logger.log('VOLUNTEER (share this link): ' + vol.getPublishedUrl());
  Logger.log('VOLUNTEER (edit link, keep private): ' + vol.getEditUrl());
}
