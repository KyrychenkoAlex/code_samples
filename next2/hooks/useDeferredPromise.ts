import { useRef } from "react";

interface DeferredPromise<DeferType> {
  resolve: (value: DeferType) => void;
  reject: (value: unknown) => void;
  promise: Promise<DeferType>;
}

function useDeferredPromise<DeferType>() {
  const deferRef = useRef<DeferredPromise<DeferType>>(null);

  const defer = () => {
    const deferred = {} as DeferredPromise<DeferType>;

    deferred.promise = new Promise<DeferType>((resolve, reject) => {
      deferred.resolve = resolve;
      deferred.reject = reject;
    });

    deferRef.current = deferred;

    return deferRef.current;
  };

  return { defer, deferRef: deferRef.current };
}

export default useDeferredPromise
