import { BrowserProvider } from 'ethers';
import { SiweMessage } from 'siwe';

const domain = window.location.host;
const origin = window.location.origin;
const provider = new BrowserProvider(window.ethereum);

async function getSiweMessage(address) {
  const response = await fetch('http://localhost:8000/auth/message?wallet_address=' + address);
  const data = await response.json();
  console.log(JSON.stringify(data.message));

  const siwe_message = new SiweMessage({
    scheme: data.message.scheme,
    domain: data.message.domain,
    address: data.message.address,
    uri: data.message.uri,
    version: data.message.version,
    chainId: data.message.chain_id,
    issuedAt: data.message.issued_at,
    nonce: data.message.nonce,
    statement: data.message.statement,
    expirationTime: data.message.expiration_time,
    notBeforeTime: data.message.not_before,
    requestId: data.message.request_id,
    resources: data.message.resources,
  });

  return siwe_message.prepareMessage();
}

function connectWallet () {
  provider.send('eth_requestAccounts', [])
    .catch(() => console.log('user rejected request'));
}

async function signInWithEthereum () {
  const signer = await provider.getSigner();
  const message = await getSiweMessage(
      signer.address
    );
  console.log(`Prepare message: ${JSON.stringify(message)}`);
  console.log(await signer.signMessage(message));
}

// Buttons from the HTML page
const connectWalletBtn = document.getElementById('connectWalletBtn');
const siweBtn = document.getElementById('siweBtn');
connectWalletBtn.onclick = connectWallet;
siweBtn.onclick = signInWithEthereum;
