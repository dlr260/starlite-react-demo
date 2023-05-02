import React from 'react'
import { useRef, useState } from "react";

function NavBar(props) {
    const navRef = props.navRef
    const submitHook = props.submitHook
    return (
        <>
        <div className="navbar bg-base-100">
            <div className="flex-1">
                <button className="btn btn-ghost normal-case text-xl">VM Uncovered</button>
            </div>
            <div className="flex-none gap-2">
                <div className="form-control">
                    <form onSubmit={submitHook}>
                    <input ref={navRef} type="text" placeholder="Search" className="input input-md input-bordered input-neutral" />
                    </form>
                </div>
            </div>
        </div>
        </>
    )
}

function ResultTemplate(props) {
    const result = props.result;

    let wines = null;
    let title = null;

    let bodyCard = (
        <>
        <p>
            Turn Shiraz 2020 - <span className="italic">Black Market Deal #43034 </span> 
            into <span className="italic">Haselgrove Tusail Shiraz 2020</span>
        </p>
        <p>Take the guesswork out of buying from Vinomofo's "Black Market" wines.</p>
        <p>Paste the offer id (eg 43034) or product page URL into the search box above to identify the real product name.</p>
        </>
    )

    if (!result) {
        return <CardTemplate body={bodyCard} />
    } else if ('errors' in result) {
        title = "Sorry..."
        bodyCard = <p>I couldn't find a match for {result.errors.offerId}. Try something else.</p>
    } else {
	if (result.wines.length > 1) {
        title = <a href={result.url} className="link link-hover" rel="noreferrer" target="_blank"> {result.name} </a>
	wines = result.wines.map((wine) => <p>{wine.name}</p>)
	} else {
        title = <a href={result.url} className="link link-hover" rel="noreferrer" target="_blank"> {result.sku_name} </a>
	}
        bodyCard = (
            <>
	    {wines}
            <p> Vintage <span className="font-semibold">{result.vintage}</span> </p>
            <p> Bottle Size <span className="font-semibold">{result.variant}</span> </p>
            <p> Varietal <span className="font-semibold">{result.varietal}</span> </p>
            <p> Region <span className="font-semibold">{result.region}, {result.country}</span> </p>
            <p> Closure <span className="font-semibold">{result.closure}</span> </p>
            <p className="italic">{result.summary}</p>
            </>
        )
    }

    return <CardTemplate body={bodyCard} title={title} />
}

function CardTemplate(props) {
    const title = props.title ? props.title : 'VM Uncovered'
    return (
        <>
        <div className="card lg:card-side bg-base-200 shadow-xl">
            <div className="card-body">
                <h2 className="card-title">{title}</h2>
                {props.body}
            </div>
        </div>
        </>
    )
}

function PageBody() {
    const [result, setResult] = useState(() => {return null})

    const remoteEndpoint = process.env.REACT_APP_API_HOST;
    const searchTerm = useRef(null);

    const handleSubmit = event => {
        const offerId = searchTerm.current.value;
        if (offerId) {
	    const url = `${remoteEndpoint}?offer_id=${encodeURIComponent(offerId)}`
	    console.log(url)
	    // fetch(remoteEndpoint+offerId.toString(),
            fetch(url,
                {mode: 'cors'}
                ).then((response) => response.json())
                 .then((data) => {
                    console.log(data);
                    setResult(data);
                })
                 .catch((error) => {
                    console.log(error.toString());
                    // Display some message to the user
                    const errObj = {
                        errors: {
                            'offerId': offerId
                        }
                    };
                    setResult(errObj)
                 })
        } else {
            setResult(null);
        }
        event.preventDefault();
    }

    return (
        <>
        <NavBar navRef={searchTerm} submitHook={handleSubmit}/>
        <ResultTemplate result={result} />
        </>
        )
        
    
}

function VinomofoPage() {
    return (
        <>
        <div className="container mx-auto space-y-2">
        <PageBody />
        </div>
        </>
    )
}

export default VinomofoPage;
