// Builds the instructions sent to the image model. Shared by the browser page and server.js,
// so the prompt the customer can inspect is exactly the one the server sends.
(function (root) {
  const CAT_LABEL = { top: 'top', bottom: 'trousers', shoes: 'shoes', acc: 'accessory' };

  // items: [{cat, ai}] in the same order their photos are attached after the person photo.
  function tryOnPrompt({ mode, items }) {
    const lines = items.map((p, i) => `- Image ${i + 2} (${CAT_LABEL[p.cat] || 'item'}): ${p.ai}`);
    const hasShoes = items.some(p => p.cat === 'shoes');
    const person = mode === 'self'
      ? 'Image 1 is a real customer photo. Keep this exact person: same face, identity, skin tone, hairstyle, facial hair, glasses, body shape and proportions. Do not beautify or change their features.'
      : 'Image 1 is our virtual model. Keep this exact person: same face, identity, skin tone, hairstyle, facial hair, body shape and proportions.';
    return [
      'Photorealistic full-body e-commerce fashion photo for an online clothing store.',
      person,
      'Dress the person in the garments shown in the other images, replacing whatever they wear in those areas:',
      ...lines,
      'Reproduce every garment faithfully: identical colour, fabric texture, prints, graphics, logos and their placement, cut, fit (oversized, wide-leg, etc.) and length. Natural fabric folds and drape on this body. Ignore any people, hands or backgrounds that appear in the garment photos.',
      hasShoes ? '' : (mode === 'self' ? 'Keep the person\'s own shoes if visible; otherwise plain white leather sneakers.' : 'Plain white leather sneakers.'),
      'Pose: standing straight facing the camera, arms relaxed at the sides, neutral confident expression.',
      'Seamless light-grey studio background, soft even lighting, sharp focus, whole body visible from head to shoes, vertical 3:4 framing.',
      'No text, no watermark, no extra people.'
    ].filter(Boolean).join('\n');
  }

  function sideViewPrompt() {
    return [
      'Image 1 shows a person wearing an outfit.',
      'Create a second photo of the SAME person in the SAME outfit: identical face, hair, garments, colours, prints, fit and shoes.',
      'New pose: relaxed three-quarter view turned slightly to the side, one hand in the trouser pocket, looking off-camera.',
      'Same seamless light-grey studio background and lighting, whole body visible from head to shoes, vertical 3:4 framing, photorealistic. No text, no watermark.'
    ].join('\n');
  }

  function modelPrompt(model) {
    return [
      `Photorealistic full-body studio photo of a fictional person who does not resemble any real or famous individual: ${model.prompt}.`,
      'Wearing a plain fitted light-grey t-shirt, plain dark-grey straight trousers and plain white sneakers.',
      'Standing straight facing the camera, arms relaxed at the sides, neutral friendly expression.',
      'Seamless light-grey studio background, soft even lighting, whole body visible from head to feet, vertical 3:4 framing. No text, no watermark.'
    ].join('\n');
  }

  const api = { tryOnPrompt, sideViewPrompt, modelPrompt };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.TryOnPrompt = api;
})(typeof self !== 'undefined' ? self : this);
