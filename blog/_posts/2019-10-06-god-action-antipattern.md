---
title: The god action anti-pattern in Redux
layout: post
---

The "god action" is an anti-pattern in Redux where an action has the ability to update all the keys of a state. Here's what that might look like in TypeScript:

```typescript
interface State {
  key1: string;
  key2: string;
  // potentially many other keys
  keyN: string;
}

type Action = { type: "GOD_ACTION"; payload: Partial<State> };

const reducer = (state: State, action: Action) => {
  switch (action.type) {
    case "GOD_ACTION":
      return {
        ...state,
        ...action.payload
      };
    // and so on
  }
};
```

The key pieces to notice are:

1. The god action payload can include *any* piece of sub-state
2. The god action reducer can update *any* piece of sub-state (or even the entire state)

## This makes it hard to understand your app state

The god action anti-pattern makes it impossible to understand the potential states and state transitions of an app by looking at the reducer.

Instead, you have to find all of the components which `dispatch` the god action and keep track of which keys are being updated from each component in response to which events. As the number of god actions dispatched grows, this becomes more difficult.

Even then, it may be impossible to comprehend all the different states and state transitions in your app since it will probably depend on the order the actions are dispatched at run time.

This is a big problem. Now your app behaves unpredictably and can reach invalid states in ways that are very hard to foresee.

## It creates opportunities for writing state bugs

This pattern is also a trip hazard when adding new features.

Whenever you need to update state in your app with a god action you can simply write:
```typescript
dispatch({ type: "GOD_ACTION", payload: { ... } });
```
without ever looking at the reducer.

This leads to state transitions not being properly considered. Pieces of state which should be invalidated are not, and side effects which should be triggered are forgotten.

## Where would you find this anti-pattern?

At first, the god action can seem like a nice way to reduce boilerplate when a component needs to update lots of individual state properties in response to lots of different events.

You might see this particularly in forms, where different inputs are bound to different state keys. Rather than write an action and reducer for each input and state key pair, it's tempting to use a god action.

We made this mistake in the [multi-page form in our signup journey](https://join.bulb.co.uk) that we have at [Bulb](https://join.bulb.co.uk). We used a god action to dispatch all the input changes to our form state, which has lead to loads of subtle state bugs.

One example is that, when updating the postcode, we forgot to also clear the address (which is no longer valid due to the location change).

If we had an `UPDATE_POSTCODE` action instead of a god action, we probably would have written a dedicated reducer which would have made the necessary state invalidations more obvious.

## Further reading

If you want to know more about how you should write actions in a maintainable way, I recommend [this talk on Action Hygiene](https://www.youtube.com/watch?v=JmnsEvoy-gY) by Mike Ryan. The talk is about `ngrx` but applies to most Redux implementations.

The [Redux style guide](https://redux.js.org/style-guide) has more information on why it's important to put logic in reducers instead of action dispatchers, and why reducers should own the state shape:
- [Put as Much Logic as Possible in Reducers](https://redux.js.org/style-guide/#put-as-much-logic-as-possible-in-reducers)
- [Reducers Should Own the State Shape](https://redux.js.org/style-guide/#reducers-should-own-the-state-shape)